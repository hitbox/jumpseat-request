"""
Receive and confirm email verification codes.
"""
from operator import attrgetter

import click

from flask import Blueprint
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from markupsafe import Markup

from jumpseat_request import settings
from jumpseat_request.extension import db
from jumpseat_request.extension import email_verify
from jumpseat_request.extension import timezone
from jumpseat_request.form import VerifyEmailForm
from jumpseat_request.frontend import airline_label_getter
from jumpseat_request.model import Airline
from jumpseat_request.model import EmailJob
from jumpseat_request.model import Employee
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import User
from jumpseat_request.model_choice import ModelChoice

email_verification_bp = Blueprint('email_verification', __name__, url_prefix='/email-verification')

user_value = attrgetter('email_address')

@email_verification_bp.route('/verify/<token>')
def verify_email(token):
    data, error = email_verify.load_token(token)
    if error:
        abort(400, description=error)

    user = db.session.get(User, {'id': data['user_id']})
    if not user:
        abort(404, 'User not found')

    if user.email_address != data['email']:
        abort(400, 'Email mismatch')

    jumpseat_request_id = data.get('jumpseat_request_id')
    ident = {'id': jumpseat_request_id}
    jumpseat_request = db.session.get(JumpseatRequest, ident)
    if not jumpseat_request:
        abort(404, f'Jumpseat request id {jumpseat_request_id} not found.')

    if user.employee is None:
        # Create employee from jumpseat request and associate it with the user.
        user.employee = Employee(
            airline = jumpseat_request.employee_airline,
            name = jumpseat_request.employee_name,
            employee_number = jumpseat_request.employee_number,
            phone = jumpseat_request.employee_phone,
        )
        flash('New employee object created and associated with user.', 'success')

    user.confirm_email()
    if user.is_guest:
        # A guest just confirmed their email address.
        # Require guest now set a password
        user.is_guest = False
        user.reset_password = True

    db.session.commit()
    flash(f'User\'s email verified at {user.email_verified_at.strftime(settings.datetime_format())}', 'success')

    flash(f'New user created from guest account. Please set your password.')
    return redirect(url_for('auth.change_password', user_id=user.id))

@email_verification_bp.route('/send-verification/<user_id>', methods=['GET', 'POST'])
def send_verification(user_id):
    user = db.session.get(User, {'id': user_id})
    if not user:
        abort(404, 'User not found')

    form = VerifyEmailForm(obj=user)

    if form.validate_on_submit():
        token = email_verify.create_token(user.email_address, user_id)

        verify_url = url_for(".verify_email", token=token) 

        email_job = EmailJob.create_email_verification(user=user, token=token)
        db.session.add(email_job)
        db.session.commit()
        flash('Email verification created', 'success')

        return redirect(url_for('jumpseat_request.landing_page'))

    context = {
        'form': form,
        'help': 'Navigate away from page to avoid email notification.',
    }
    return render_template('form.html', **context)
