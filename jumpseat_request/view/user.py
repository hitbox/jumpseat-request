import click

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import logout_user
from markupsafe import Markup

from jumpseat_request.authenticate import login_and_password_ok
from jumpseat_request.extension import db
from jumpseat_request.form import EditAccountForm
from jumpseat_request.form import RegisterUserForm
from jumpseat_request.form import form_obj_diff
from jumpseat_request.guest import get_current_user_or_create_guest
from jumpseat_request.model import User

from htmlkit.lists import definition_list

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/edit-account/<user_id>', methods=['GET', 'POST'])
@login_and_password_ok
def edit_account(user_id):
    """
    Current logged in user edit their account info.
    """
    user = db.session.get(User, {'id': user_id})
    if not user:
        abort(404, 'User not found')

    form = EditAccountForm(obj=user)

    if form.validate_on_submit():
        changes = form_obj_diff(form, user)
        if changes:
            changes = {key: f'{from_} -> {to}' for key, (from_, to) in changes.items()}
            flash(Markup('<p>Account changed</p>') + definition_list(changes, class_='table'), 'success')
        form.populate_obj(user)
        db.session.commit()
        if user.email_verified_at is None:
            flash('Account email changed. Send verification again?')
            # Redirect to send verification
            send_verify_url = url_for(
                'email_verification.send_verification',
                user_id=user_id
            )
            return redirect(send_verify_url)

    context = {
        'user': user,
        'form': form,
    }

    return render_template('form.html', **context)

@user_bp.route('/new-account', methods=['GET', 'POST'])
@click.option('--is-guest', is_flag=True, default=False)
def create_account(is_guest):
    """
    Allow user to create account.
    """
    form = RegisterUserForm()

    if form.validate_on_submit():
        new_user = User(
            email_address = form.employee.email_address.data,
            is_guest = is_guest,
        )

    context = {
        'form': form,
    }
    return render_template('form.html', **context)

@user_bp.route('/register/<guest_token>', methods=['POST', 'GET'])
def register_new_user(guest_token):
    """
    Allow user to create an account.
    """
    # Get guest data from session
    guest = get_current_user_or_create_guest()
    register_form = RegisterUserForm(
        email_address = guest.email_address,
    )

    if request.method == 'POST':
        if register_form.validate():
            new_user = User(
                email_address = register_form.email_address.data
            )
            db.session.add(new_user)
            raise NotImplementedError('Insert email verification here')
            db.session.add(verify)
            db.session.commit()
            # redirect to form to verify secret
            url = url_for(
                'email_verification.verify_email',
                user_id=new_user.id,
            )
            response = redirect(url)
            current_app.logger.debug('confirm hash: %s', code)
            flash('New user and verification code created', 'info')
            return response

    context = {
        'register_form': register_form,
    }

    return render_template('register.html', **context)

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
