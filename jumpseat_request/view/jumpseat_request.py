import random
import string
import uuid

from datetime import date
from functools import wraps

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session as flask_session
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from markupsafe import Markup

from jumpseat_request import settings
from jumpseat_request import signal
from jumpseat_request.authenticate import login_and_password_ok
from jumpseat_request.extension import db
from jumpseat_request.extension import login_manager
from jumpseat_request.extension import timezone
from jumpseat_request.form import JumpseatRequestActionForm
from jumpseat_request.form import EditJumpseatRequestForm
from jumpseat_request.form import LoginForm
from jumpseat_request.guest import get_current_user_or_create_guest
from jumpseat_request.model import Airline
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import User
from jumpseat_request.schema import JumpseatRequestDataSchema

jumpseat_request_bp = Blueprint('jumpseat_request', __name__, url_prefix='/jumpseat')

request_data_schema = JumpseatRequestDataSchema()

def require_is_decider(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not getattr(current_user, 'is_decider', False):
            abort(
                403,
                description = f'Logged in account {current_user.email_address} does'
                    ' not have permission to decide requests.'
            )

        return func(*args, **kwargs)
    return wrapped

@jumpseat_request_bp.route('/decide/<request_id>', methods=['GET', 'POST'])
@login_and_password_ok
def decide_jumpseat_request(request_id):
    """
    Approve a jump seat request proposal from a user or guest.
    """
    # require decider-user login
    if not current_user.is_decider:
        abort(
            403,
            description = f'Logged in account {current_user.email_address} does'
                ' not have permission to decide requests.'
        )

    jumpseat_request = db.session.get(JumpseatRequest, request_id)
    if not jumpseat_request:
        abort(404, description='Request not found')

    if not jumpseat_request.is_undecided():
        abort(404, description=f'Jumpseat request status {jumpseat_request.status()}')

    form = JumpseatRequestActionForm(obj=jumpseat_request)
    if form.validate_on_submit():
        form.populate_obj(jumpseat_request)
        db.session.commit()
        flash('Request updated', 'success')
        signal.jumpseat_request_decided.send(
            # sender is first positional arg
            request.endpoint,
            signal = signal.jumpseat_request_decided,
            jumpseat_request = jumpseat_request,
        )
        return redirect(url_for('.list_jumpseat_requests'))

    context = {
        'form': form,
        'extra': jumpseat_request.html_card(),
    }
    return render_template('edit_form.html', **context)

@jumpseat_request_bp.route('/list-requests', methods=['GET'], defaults={'request_id': None})
@jumpseat_request_bp.route('/list-requests/<request_id>', methods=['POST'])
@require_is_decider
def list_jumpseat_requests(request_id):
    """
    Paginated list of jump seat requests and a form for each to approve or deny.
    """
    # No login required.
    if not current_user.is_decider:
        abort(
            403,
            description = f'Logged in account {current_user.email_address} does'
                ' not have permission to decide requests.'
        )

    query = (
        db.select(JumpseatRequest)
        .where(
            ~JumpseatRequest.is_decided,
        )
        .order_by(
            JumpseatRequest.created_at.desc(),
        )
    )
    pagination = db.paginate(query)

    forms = {
        str(request.id): JumpseatRequestActionForm(obj=request)
        for request in pagination
    }

    if request_id:
        jumpseat_request = db.session.get(JumpseatRequest, request_id)
        form = forms[request_id]
        form.process(request.form)
        if form.validate_on_submit():
            form.populate_obj(jumpseat_request)
            db.session.commit()
            flash('Request updated', 'success')
            return redirect(url_for('.list_jumpseat_requests'))

    context = {
        'pagination': pagination,
        'forms': forms,
    }

    return render_template('decide.html', **context)

def get_data_for_random_autofill():
    fnumber = ''.join(random.choices(string.digits, k=4))
    eenumber = ''.join(random.choices(string.digits, k=4))
    phonedigit = random.choice(string.digits)
    data = {
        'flight_date': date.today(),
        'flight_number': fnumber,
        'employee_number': f'EE{eenumber}',
        'employee_name': f'First{eenumber} Last',
        'employee_phone': phonedigit * 3 + ' ' + phonedigit * 3 + ' ' + phonedigit * 4
    }

    if current_user.is_authenticated:
        data['employee_email'] = current_user.email_address
    else:
        data['employee_email'] = f'user{eenumber}@company.com'
    return data

def get_data_for_current_user():
    # Dictionary keys must match EditJumpseatRequestForm attribute names.
    data = {
        'employee_email': current_user.email_address,
    }
    if current_user.employee:
        employee = current_user.employee
        data.update({
            'employee_airline': employee.airline,
            'employee_number': employee.employee_number,
            'employee_name': employee.name,
            'employee_phone': employee.phone,
        })
    return data

@jumpseat_request_bp.route('/', methods=['GET', 'POST'])
def landing_page():
    """
    Logged in or anonymous user landing page for requesting a jumpeseat and
    viewing their submitted requests.
    """
    request_by = current_user

    if 'randomfill' in request.args:
        jumpseat_request_form = EditJumpseatRequestForm(data=get_data_for_random_autofill())
    else:
        if current_user.is_authenticated:
            data = get_data_for_current_user()
        else:
            data = {}
        jumpseat_request_form = EditJumpseatRequestForm(data=data)

    if jumpseat_request_form.validate_on_submit():
        email_address = jumpseat_request_form.employee_email.data
        request_by = get_current_user_or_create_guest(email_address=email_address)
        assert request_by is not None
        jumpseat_request = JumpseatRequest(
            request_by = request_by,
        )
        db.session.add(jumpseat_request)
        jumpseat_request_form.populate_obj(jumpseat_request)
        # Call again for submit, with email from form to create guest if
        # necessary.

        db.session.flush()
        flash('Jumpeat Request Created', 'success')

        # Send signal for jumpseat request created.
        signal.jumpseat_request_created.send(
            # sender is first positional arg
            request.endpoint,
            signal = signal.jumpseat_request_created,
            jumpseat_request = jumpseat_request,
        )
        db.session.commit()

        # Redirect to ourself
        return redirect(url_for(request.endpoint))

    context = {
        'form': jumpseat_request_form,
        'request_by': request_by,
    }
    context.update(settings.context())

    # query for current user's requests.
    if isinstance(request_by, User):
        jumpseat_request_query = (
            db.select(JumpseatRequest)
            .where(
                JumpseatRequest.request_by == request_by
            )
        )

        # Create list of jumpseat requests by the current user or guest.
        current_requests = db.session.scalars(jumpseat_request_query).all()

        context['current_requests'] = current_requests

    return render_template('landing.html', **context)
