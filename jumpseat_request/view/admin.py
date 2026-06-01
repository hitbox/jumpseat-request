import click
import sqlalchemy as sa

from flask import Blueprint
from flask import url_for
from flask_login import current_user

from jumpseat_request.extension import db
from jumpseat_request.model import Airline
from jumpseat_request.model import ContactMethod
from jumpseat_request.model import ContactMethodType
from jumpseat_request.model import ContactType
from jumpseat_request.model import Employee
from jumpseat_request.model import Identity
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import Provider
from jumpseat_request.model import User
from jumpseat_request.seed import seed_database

from .pluggable import TableEditor

from htmlkit.lists import unordered_list
from htmlkit.table import Column
from htmlkit.table import Table

model_classes = [
    Airline,
    ContactMethod,
    ContactMethodType,
    Employee,
    Identity,
    JumpseatRequest,
    Provider,
    User,
]

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

admin_bp.cli.help = 'Administration command line commands.'

@admin_bp.before_request
def require_admin_login():
    if not current_user.is_authenticated:
        flash('Login to access admin.', 'info')
        return redirect(url_for(login_manager.login_view, next=request.full_path))
        if not current_user.is_admin:
            flash('Admin required.', 'danger')
            return redirect(url_for(login_manager.login_view, next=request.full_path))

@admin_bp.cli.command('create-db')
def create_db():
    """
    Create database schema.
    """
    db.create_all()

@admin_bp.cli.command('seed-db')
def seed_db():
    """
    Seed database with necessary data.
    """
    seed_database()

@admin_bp.route('/')
def root():
    items = []
    for subname in names:
        url = url_for(f'admin.{subname}')
        item = f'<a href="{url}">{subname}</a>'
        items.append(item)
    response = unordered_list(items)
    return response

class PaginationGetter:

    def __init__(self, func):
        self.func = func

    def __call__(self):
        return self.func()

names = []
for model_class in model_classes:
    pagination_getter = lambda model_class: db.paginate(db.select(model_class))
    mapper = db.inspect(model_class)

    table = Table.from_model(model_class)

    init_args = [
        'admin_table.html',
        model_class,
        pagination_getter,
        table,
    ]
    name = model_class.__tablename__
    names.append(name)
    admin_bp.add_url_rule(
        f'/{name}',
        view_func = TableEditor.as_view(name, *init_args)
    )
