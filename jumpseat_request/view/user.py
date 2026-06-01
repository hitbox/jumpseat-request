import click

from flask import Blueprint

from jumpseat_request.extension import db
from jumpseat_request.model import Provider
from jumpseat_request.model import User

user_bp = Blueprint('user', __name__, url_prefix='/user')

user_bp.cli.help = 'Administrate user accounts'

@user_bp.cli.command('delete')
@click.argument('username')
def delete_user(username):
    """
    Delete user account.
    """
    user = User.by_username(username)
    if user is None:
        raise ValueError(f'Username not found: {username}')

    db.session.delete(user)
    db.session.commit()
    click.echo(f'{username} deleted')

@user_bp.cli.command('create')
@click.option('--username', required=True)
@click.password_option('--password', required=True)
@click.option('--is-admin', is_flag=True)
@click.option('--disabled', is_flag=True, help='Create user as disabled')
def create_user(username, password, is_admin, disabled):
    """
    Create a new user account for application.
    """
    user = User.create(
        username = username,
        password_text = password,
        is_admin = is_admin,
        is_active = not disabled,
    )
    db.session.add(user)
    db.session.commit()

@user_bp.cli.command('test')
@click.argument('username')
@click.password_option('--password', required=True)
def test_user(username, password):
    """
    Test password for user account.
    """
    user = User.by_username(username)
    if user is None:
        raise ValueError(f'Username not found: {username}')
    if user.check_password(password):
        click.echo('Password success')
    else:
        click.echo('Password failed')
