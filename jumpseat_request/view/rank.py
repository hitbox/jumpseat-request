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
from jumpseat_request.model import Rank

from htmlkit.lists import definition_list

rank_bp = Blueprint('rank', __name__, url_prefix='/rank')

rank_bp.cli.help = 'Administrate rank objects'

@rank_bp.cli.command('delete')
@click.argument('rank-code')
def delete_user(rank_code):
    """
    Delete user account.
    """
    rank = Rank.by_code(rank_code)
    if rank is None:
        raise ValueError(f'Rank object not found: {rank_code}')

    db.session.delete(rank)
    db.session.commit()
    click.echo(f'{rank} object deleted')

@rank_bp.cli.command('create')
@click.option('--rank-code', required=True)
@click.option('--rank-name')
@click.option('--if-not-exists', is_flag=True)
def create_user(rank_code, rank_name, if_not_exists):
    """
    """
    rank = Rank.by_code(rank_code)
    if rank and not if_not_exists:
        raise ValueError(f'{rank_code} already exists')

    rank = Rank(
        code = rank_code,
        name = rank_name,
    )
    db.session.add(rank)
    db.session.commit()
