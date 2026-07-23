import calendar
import random
import string
import uuid

from datetime import date
from datetime import datetime

import click

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
from jumpseat_request.extension import db
from jumpseat_request.extension import login_manager
from jumpseat_request.extension import timezone
from jumpseat_request.form import EditJumpseatRequestForm
from jumpseat_request.form import JumpseatRequestActionForm
from jumpseat_request.form import LoginForm
from jumpseat_request.guard import require_is_decider
from jumpseat_request.guard import require_password_ok
from jumpseat_request.guard import response_for_reset_password
from jumpseat_request.model import Airline
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import Leg
from jumpseat_request.model import User
from jumpseat_request.query import ranked_legs
from jumpseat_request.query import newest_leg_scheduled_flights

jumpseat_request_bp = Blueprint('jumpseat_request', __name__, url_prefix='/jumpseat')

def action_forms_by_id(jumpseats):
    """
    Jump Seat actions forms indexed by a list of jumpseat object ids.
    """
    forms = {
        str(request.id): JumpseatRequestActionForm(obj=request)
        for request in jumpseats
    }
    return forms

@jumpseat_request_bp.route('/decide/<request_id>', methods=['GET', 'POST'])
@require_password_ok
@require_is_decider
def decide_jumpseat_request(request_id):
    """
    Approve a jump seat request proposal from a user or guest.
    """
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
        'jumpseat_request': jumpseat_request,
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
    forms = action_forms_by_id(pagination)

    if request_id:
        jumpseat_request = db.session.get(JumpseatRequest, request_id)
        form = forms[request_id]
        form.process(request.form)
        if form.validate_on_submit():
            form.populate_obj(jumpseat_request)
            db.session.commit()
            signal.jumpseat_request_decided.send(
                # sender is first positional arg
                request.endpoint,
                signal = signal.jumpseat_request_decided,
                jumpseat_request = jumpseat_request,
            )
            flash('Request updated', 'success')
            return redirect(url_for(request.endpoint))

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
        'flight_datetime': datetime.now(),
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

@jumpseat_request_bp.route('/select-calendar')
def select_calendar():
    context = {
        'calendar': calendar,
        'current_month': timezone.today().month,
    }

    selected_month = int(request.args.get('month', '0'))

    months = []
    for month_num in range(1, 13):
        month = {
            'name': calendar.month_name[month_num],
            'number': month_num,
        }

        if selected_month > 0:
            query = newest_leg_scheduled_flights
            query = query.where(
                db.func.extract('month', ranked_legs.c.dep_sched_dt) == month_num,
                ranked_legs.c.fn_carrier == 'GB',
            )
            scheduled_flights = db.session.scalars(query).all()

            month.update({
                'scheduled_flights': scheduled_flights,
            })

            dates = set([leg.dep_sched_date for leg in scheduled_flights])
            dates_rel = {}
            for date in dates:
                next_date = min((d for d in dates if d > date), default=None)
                prev_date = max((d for d in dates if d < date), default=None)
                dates_rel.update({
                    date: {
                        'next_date': next_date,
                        'prev_date': prev_date,
                    },
                })

        context.update({
            'months': months,
        })

    return render_template('select-calendar.html', **context)

@jumpseat_request_bp.route('/', methods=['GET', 'POST'])
@require_password_ok
@login_required
def landing_page():
    """
    Logged in user can request a jumpseat.
    """
    context = {}
    request_by = current_user

    if 'randomfill' in request.args:
        jumpseat_request_form = EditJumpseatRequestForm(data=get_data_for_random_autofill())
    else:
        if current_user.is_authenticated:
            data = get_data_for_current_user()
        else:
            data = {}
        jumpseat_request_form = EditJumpseatRequestForm(data=data)

    if 'fn_number' in request.args and 'dep_sched_dt' in request.args:
        # fn_number is integer from lufthansa
        selected_fn_number = int(request.args['fn_number'])
        jumpseat_request_form.flight_number.data = selected_fn_number
        selected_dep_sched_dt = datetime.fromisoformat(request.args['dep_sched_dt'])
        jumpseat_request_form.flight_datetime.data = selected_dep_sched_dt
        flash(f'Flight info filled from selected.', 'info')

    if jumpseat_request_form.validate_on_submit():
        email_address = jumpseat_request_form.employee_email.data
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

    context.update({
        'form': jumpseat_request_form,
        'request_by': request_by,
        'calendar': calendar,
    })
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

@jumpseat_request_bp.cli.command('query')
@click.option('--month', type=int)
def query(month):
    """
    Quick way to test query on command line.
    """
    query = newest_leg_scheduled_flights

    if month is not None:
        query = query.where(
            db.func.extract('month', ranked_legs.c.day_of_origin) == month,
        )

    click.echo(query)

    click.confirm('Continue?', default=True)

    for leg in db.session.scalars(query):
        click.echo(leg.__dict__)
