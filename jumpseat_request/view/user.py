import click

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import logout_user
from markupsafe import Markup

from jumpseat_request.extension import db
from jumpseat_request.form import EditAccountForm
from jumpseat_request.form import RegisterUserForm
from jumpseat_request.form import VerifyEmailForm
from jumpseat_request.form import form_obj_diff
from jumpseat_request.guard import login_and_password_ok
from jumpseat_request.model import User
from jumpseat_request.signal import account_creation_requested

from htmlkit.lists import definition_list

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_and_password_ok
def profile():
    """
    current_user profile page
    """
    edit_account_form = EditAccountForm(obj=current_user)

    if edit_account_form.validate_on_submit():
        edit_account_form.populate_obj(current_user)
        db.session.commit()
        flash('Profile updated', 'info')
        return redirect(url_for(request.endpoint))

    context = {
        'edit_account_form': edit_account_form,
    }
    return render_template('profile.html', **context)

@user_bp.route('/new-account', methods=['GET', 'POST'])
def create_account():
    """
    Allow user to create account.
    """
    form = VerifyEmailForm()

    if form.validate_on_submit():
        email_address = form.email_address.data
        exists = User.by_email(email_address)
        if exists:
            url = url_for(
                '.send_email_verification',
                email_address=email_address,
                next = url_for(request.endpoint),
            )
            flash(
                Markup(
                    f'<p class="warning message">Email address {email_address} already exists.</p>'
                    f'<a href="{url}">Click to send another verfication link.</a>'
                ),
                'warning',
            )
        else:
            account_creation_requested.send(
                create_account,
                email_address = form.email_address.data,
            )
            flash('You should receive a verification link in your inbox soon', 'info')

    context = {
        'form': form,
    }
    return render_template('create_account.html', **context)

@user_bp.route('/send-verification/<email_address>')
def send_email_verification(email_address):
    account_creation_requested.send(
        create_account,
        email_address = email_address,
    )
    flash('You should receive a verification link in your inbox soon', 'info')

    url = request.args.get('next', url_for('.create_account'))
    return redirect(url)

user_bp.cli.help = 'Administrate user accounts'

def get_user_or_abort(email_address):
    query = (
        db.select(User)
        .where(
            User.email_address == email_address
        )
    )
    user = db.session.scalars(query).one_or_none()
    if not user:
        click.echo(f'User {email_address} not found')
        raise click.Abort()

    return user

@user_bp.cli.command('delete')
@click.argument('email_address')
def delete_user(email_address):
    """
    Delete user account.
    """
    user = User.by_username(email_address)
    if user is None:
        raise ValueError(f'Username not found: {email_address}')

    db.session.delete(user)
    db.session.commit()
    click.echo(f'{email_address} deleted')

@user_bp.cli.command('create')
@click.option('--email', required=True)
@click.password_option('--password', required=True)
@click.option('--is-admin', is_flag=True)
@click.option('--is-guest', is_flag=True)
@click.option('--is-decider', is_flag=True)
@click.option('--disabled', is_flag=True, help='Create user as disabled')
@click.option('--is-verified', is_flag=True, help='Mark user\'s email address as verified.')
def create_user(email, password, is_admin, is_guest, is_decider, disabled, is_verified):
    """
    Create a new user account for application.
    """
    user = User(
        email_address = email,
        password_hash = password,
        is_admin = is_admin,
        is_active = not disabled,
        is_decider = is_decider,
        is_guest = is_guest,
    )
    if is_verified:
        user.confirm_email()
    db.session.add(user)
    db.session.commit()

@user_bp.cli.command('checkpass')
@click.argument('email_address')
@click.password_option('--password', required=True)
def checkpass(email_address, password):
    """
    Test password for user account.
    """
    query = (
        db.select(User)
        .where(
            User.email_address == email_address
        )
    )
    user = db.session.scalars(query).one_or_none()
    if not user:
        click.echo(f'User {email_address} not found')
        raise click.Abort()

    if user.check_password(password):
        click.echo('Password success')
    else:
        click.echo('Password failed')

@user_bp.cli.command('logout')
def logout():
    """
    Command-line way to logout user.
    """
    logout_user()
