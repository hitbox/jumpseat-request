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
from flask_login import login_required
from flask_login import logout_user
from markupsafe import Markup

from jumpseat_request.extension import db
from jumpseat_request.model import JumpseatRequestPriority

from htmlkit.lists import definition_list

priority_bp = Blueprint('rank', __name__, url_prefix='/rank')

priority_bp.cli.help = 'Administrate rank objects'

def get_by_name(name):
    query = (
        db.select(JumpseatRequestPriority)
        .where(
            JumpseatRequestPriority.name == name
        )
    )
    priority = db.session.scalars(query).one_or_none()
    return priority

@priority_bp.cli.command('delete')
@click.argument('name')
def delete(name):
    """
    Delete jumpseat priority by name.
    """
    priority = get_by_name(name)
    if priority is None:
        raise ValueError(f'Priority object not found: {name}')

    db.session.delete(priority)
    db.session.commit()
    click.echo(f'{priority} object deleted')

@priority_bp.cli.command('create')
@click.option('--name', required=True)
@click.option('--if-not-exists', is_flag=True)
def create(name, if_not_exists):
    """
    """
    priority = get_by_name(name)
    if priority and not if_not_exists:
        raise ValueError(f'{priority} already exists')

    priority = JumpseatRequestPriority(
        name = name,
    )
    db.session.add(priority)
    db.session.commit()
