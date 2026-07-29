import calendar
import random
import string
import uuid

from datetime import date
from datetime import datetime
from datetime import timedelta
from itertools import groupby
from operator import attrgetter
from operator import itemgetter

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
from jumpseat_request.calendar import build_calendar
from jumpseat_request.db_compat import trunc_date
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
from jumpseat_request.model import Employee
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import Leg
from jumpseat_request.model import User
from jumpseat_request.query import LegRanked
from jumpseat_request.query import counts_after_date
from jumpseat_request.query import counts_by_date
from jumpseat_request.query import newest_leg_scheduled_flights
from jumpseat_request.query import ranked_legs
from jumpseat_request.settings import scheduled_flight_carrier

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
        abort(404, description=f'Jumpseat request already decided: status {jumpseat_request.status()}')

    form = JumpseatRequestActionForm(obj=jumpseat_request)
    if not jumpseat_request.is_undecided():
        del form.approve
        del form.deny
        flash(f'Request already decided. {jumpseat_request.status()}')

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
            description = f'Logged in account does'
                ' not have permission to decide requests (is_decider flag).'
        )

    query = (
        db.select(JumpseatRequest)
        .where(
            db.not_(JumpseatRequest.is_decided),
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

def ensure_date(value):
    if isinstance(value, datetime):
        value = value.date()
    return value

@jumpseat_request_bp.route('/select-calendar')
def select_calendar():
    """
    Yearly calendar to select date for scheduled flights.
    """
    today = timezone.today()

    months = build_calendar(today.year, today=today)

    query = counts_after_date(today)

    # mapping dates -> count of scheduled flights
    counts_for_date = {
        ensure_date(row.date): row.count
        for row in db.session.execute(query)
    }

    context = {
        'today': timezone.today(),
        'months': months,
        'counts_for_date': counts_for_date,
        'scheduled_flight_carrier': scheduled_flight_carrier(),
    }

    selected_month = int(request.args.get('month', '0'))

    return render_template('select-calendar.html', **context)

@jumpseat_request_bp.route('/select-calendar/<date:date>')
def selected_date_calendar(date):
    """
    Table listing scheduled flights for a date. Table row links to go to
    jumpseat request page with flight info filled in.
    """
    datenav = [date + timedelta(days=days) for days in range(-3, 4)]
    context = {
        'scheduled_flights': Leg.all_for_date(date),
        'month_name': calendar.month_name[date.month],
        'datenav': datenav,
    }
    return render_template('scheduled-flights.html', **context)

@jumpseat_request_bp.route('/', methods=['GET', 'POST'])
@require_password_ok
@login_required
def landing_page():
    """
    Logged in user can request a jumpseat.
    """
    context = {}
    if 'randomfill' in request.args:
        jumpseat_request_form = EditJumpseatRequestForm(data=get_data_for_random_autofill())
    else:
        if current_user.is_authenticated:
            data = get_data_for_current_user()
        else:
            data = {}
        jumpseat_request_form = EditJumpseatRequestForm(data=data)

    if current_user.employee is not None:
        # Account already associated with an employee remove option to save.
        del jumpseat_request_form.save_employee_info
        flash(f'Employee info loaded automatically.', 'info')

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
            request_by = current_user,
        )
        db.session.add(jumpseat_request)
        jumpseat_request_form.populate_obj(jumpseat_request)
        
        if (
            current_user.employee is None
            and
            jumpseat_request_form.save_employee_info.data
        ):
            employee_number = jumpseat_request_form.employee_number.data
            query = (
                db.select(Employee)
                .where(Employee.employee_number == employee_number)
            )
            exists = db.session.scalars(query).one_or_none()
            if exists:
                flash(
                    f'Employee number {employee_number} already exists.'
                    f'Contact an administrator to resolve.',
                    'danger',
                )
            else:
                employee = Employee()
                db.session.add(employee)
                jumpseat_request_form.populate_obj(employee)
                current_user.employee = employee
                flash(f'Employee information saved.')

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
        'request_by': current_user,
    })
    context.update(settings.context())

    # query for current user's requests.
    jumpseat_request_query = (
        db.select(JumpseatRequest)
        .where(
            JumpseatRequest.request_by == current_user
        )
        .order_by(
            JumpseatRequest.created_at.desc(),
        )
    )

    # Create list of jumpseat requests by the current user or guest.
    current_requests = db.session.scalars(jumpseat_request_query).all()

    context.update({
        'current_requests': current_requests,
    })

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
