from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup

from htmlkit.lists import unordered_list
from htmlkit.table import Column
from htmlkit.table import Table
from jumpseat_request.authenticate import login_and_password_ok
from jumpseat_request.extension import db
from jumpseat_request.extension import login_manager
from jumpseat_request.form import EditAnnouncementForm
from jumpseat_request.form import EditEmployeeForm
from jumpseat_request.form import EditJumpseatRequestForm
from jumpseat_request.form import EditNotificationRuleForm
from jumpseat_request.form import EditUserForm
from jumpseat_request.form import NewAnnouncementForm
from jumpseat_request.form import NewEmployeeForm
from jumpseat_request.form import NewJumpseatRequestForm
from jumpseat_request.form import NewUserForm
from jumpseat_request.form import model_class_forms
from jumpseat_request.frontend import many_formatter
from jumpseat_request.frontend import yesno
from jumpseat_request.model import Airline
from jumpseat_request.model import Announcement
from jumpseat_request.model import ApplicationSetting
from jumpseat_request.model import Employee
from jumpseat_request.model import Identity
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import JumpseatRequestNotificationRuleAssoc
from jumpseat_request.model import NotificationRule
from jumpseat_request.model import NotificationRule
from jumpseat_request.model import Provider
from jumpseat_request.model import User
from jumpseat_request.seed import seed_database

from .admin_spec import admin_specs_for_views
from .pluggable import EditObjectView
from .pluggable import ListView
from .pluggable import NewObjectView

# model classes with an admin page
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

admin_bp.cli.help = 'Administration command line commands.'

@admin_bp.before_request
def require_admin_login():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin login required.', 'danger')
        return redirect(url_for(login_manager.login_view, next=request.url))

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

def make_edit_endpoint(name, pkname='id'):
    def endpoint(obj):
        return url_for(f'admin.{name}_edit', id=getattr(obj, pkname))
    return endpoint

def make_pagination_getter(model_class):
    pagination_getter = getattr(model_class, 'pagination_getter', None)
    if pagination_getter:
        return pagination_getter

    def pagination_getter():
        return db.paginate(db.select(model_class))
    return pagination_getter

def url_for_model_list(table_name):
    def url_maker():
        return url_for(f'admin.{table_name}_list')
    return url_maker

def make_views_for_models(specs):
    """
    Add routes and rules for all model classes in the list and an index-list
    page with links to them.
    """
    links = []
    for spec in specs:
        model_class = spec['model_class']

        mapper = db.inspect(model_class)

        table_name = model_class.__tablename__
        model_name = model_class.__name__

        list_endpoint = f'{table_name}_list'

        # build up list view kwargs with optional edit/new views
        pagination_getter = spec.get('pagination_getter', make_pagination_getter(model_class))
        list_kwargs = {
            'template': spec.get('template', 'admin/table.html'),
            'table': spec['html_table'],
            'pagination_getter': pagination_getter,
            'model_class': model_class,
        }

        # Optional view for editing objects. If a edit form is not configured
        # we do not create links to editing in the list view.
        edit_form = spec.get('edit_form')
        if edit_form:
            # Callable because we need a url for each object in the list.
            edit_endpoint = make_edit_endpoint(table_name, pkname=spec.get('pkname'))
            list_kwargs.setdefault('edit_endpoint', edit_endpoint)
            after_endpoint = spec.get('edit_after_endpoint', f'admin.{table_name}_list')
            init_kwargs = {
                'template': spec.get('edit_template', 'admin/edit_form.html'),
                'model_class': model_class,
                'form_class': edit_form,
                'after_endpoint': after_endpoint,
            }
            admin_bp.add_url_rule(
                f'/{table_name}-edit/<id>',
                view_func = login_and_password_ok(
                    EditObjectView.as_view(
                        f'{table_name}_edit',
                        **init_kwargs
                    ),
                ),
            )

        new_form = spec.get('new_form')
        if new_form:
            # Full endpoint name because it will be used from the list view class.
            new_endpoint = f'admin.{table_name}_new'
            list_kwargs.setdefault('new_endpoint', new_endpoint)
            # Redirect after submit, defaulting to the list
            after_endpoint = spec.get('edit_after_endpoint', f'admin.{table_name}_list')
            init_kwargs = {
                'template': spec.get('edit_template', 'admin/edit_form.html'),
                'model_class': model_class,
                'form_class': new_form,
                'after_endpoint': after_endpoint,
            }
            admin_bp.add_url_rule(
                f'/{table_name}-new',
                view_func = login_and_password_ok(
                    NewObjectView.as_view(
                        f'{table_name}_new',
                        **init_kwargs
                    )
                )
            )

        links.append({
            'endpoint': f'admin.{list_endpoint}',
            'current_for': [f'admin.{table_name}_{last}' for last in ('list', 'edit', 'new')],
            'name': model_class.name_for_template(),
        })

        admin_bp.add_url_rule(
            f'/{table_name}-list',
            view_func = login_and_password_ok(
                ListView.as_view(
                    list_endpoint,
                    **list_kwargs
                ),
            ),
        )

    @admin_bp.app_context_processor
    def inject():
        """
        Inject context for admin navigation.
        """
        return { 'links': links }

    @admin_bp.route('/')
    def root():
        return render_template('admin/base.html')

def jumpseat_data_cast(jumpseat_request, obj):
    if obj:
        return Markup(render_template('jumpseat_request_card.html', jumpseat_request=jumpseat_request))
    else:
        return ''

def by_tablename(data):
    return data['model_class'].__tablename__

admin_specs_for_views = sorted(admin_specs_for_views, key=by_tablename)

make_views_for_models(admin_specs_for_views)
