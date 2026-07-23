"""
Receive and confirm email verification codes.
"""
from flask import Blueprint
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for

from jumpseat_request import settings
from jumpseat_request.extension import db
from jumpseat_request.extension import email_verify
from jumpseat_request.extension import timezone
from jumpseat_request.form import VerifyEmailForm
from jumpseat_request.model import EmailJob
from jumpseat_request.model import Employee
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import User

email_verification_bp = Blueprint(
    'email_verification',
    __name__,
    url_prefix = '/email-verification',
)

@email_verification_bp.route('/verify/<token>')
def verify_email(token):
    """
    Verify token from inbox link.
    """
    data, error = email_verify.load_token(token)
    if error:
        abort(400, description=error)

    email_address = data['email_address']

    user = User.by_email(email_address)
    if user:
        # Already exists update verification and force password reset.
        user.email_verified_at = timezone.now()
        user.reset_password = True
        db.session.commit()
        flash(f'Existing user email confirmed. Please set your password.')
    else:
        # Create new user from verified email link token.
        user = User(
            email_address = email_address,
            email_verified_at = timezone.now(),
            reset_password = True, # force new user to set a password
        )
        db.session.add(user)
        db.session.commit()
        flash(f'New user created. Please set your password.')

    verified_at_formatted = user.email_verified_at.strftime(settings.datetime_format())
    flash(f'User\'s email verified at {verified_at_formatted}', 'success')

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
