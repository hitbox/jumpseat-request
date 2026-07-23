from operator import attrgetter

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup

from htmlkit.core import mailto
from htmlkit.lists import unordered_list
from htmlkit.table import Column
from htmlkit.table import Table
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
from jumpseat_request.guard import login_and_password_ok
from jumpseat_request.model import Airline
from jumpseat_request.model import Announcement
from jumpseat_request.model import ApplicationSetting
from jumpseat_request.model import EmailJob
from jumpseat_request.model import Employee
from jumpseat_request.model import Identity
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import JumpseatRequestNotificationRuleAssoc
from jumpseat_request.model import NotificationRule
from jumpseat_request.model import NotificationRule
from jumpseat_request.model import Provider
from jumpseat_request.model import User
from jumpseat_request.seed import seed_database

from .admin_spec import AdminSpec
from .admin_spec import admin_specs_for_views
from .pluggable import EditObjectView
from .pluggable import ListView
from .pluggable import NewObjectView
from .pluggable import SingleView

# model classes with an admin page
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

admin_bp.cli.help = 'Administration command line commands.'

get_id = attrgetter('id')

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
        kwargs = {}
        ident = getattr(obj, pkname)
        kwargs[pkname] = ident
        return url_for(f'admin.{name}_edit', **kwargs)
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

@admin_bp.app_context_processor
def inject():
    """
    Inject context for admin navigation.
    """
    return {
        'links': [
            {
                'endpoint': 'admin.announcement_list',
                'current_for': set([
                    'admin.announcement_list',
                    'admin.announcement_edit',
                    'admin.announcement_new',
                ]),
                'name': 'Announcement',
            },
            {
                'endpoint': 'admin.user_list',
                'current_for': set([
                    'admin.user_list',
                    'admin.user_edit',
                    'admin.user_new',
                ]),
                'name': 'User',
            },
            {
                'endpoint': 'admin.employee_list',
                'current_for': set([
                    'admin.employee_list',
                    'admin.employee_edit',
                    'admin.employee_new',
                ]),
                'name': 'Employee',
            },
            {
                'endpoint': 'admin.jumpseat_request_list',
                'current_for': set([
                    'admin.jumpseat_request_list',
                    'admin.jumpseat_request_edit',
                    'admin.jumpseat_request_new',
                ]),
                'name': 'Jumpseat Request',
            },
            {
                'endpoint': 'admin.notification_rule_list',
                'current_for': set([
                    'admin.notification_rule_list',
                    'admin.notification_rule_edit',
                    'admin.notification_rule_new',
                ]),
                'name': 'Notification Rule',
            },
            {
                'endpoint': 'admin.email_job_list',
                'current_for': set([
                    'admin.email_job_list',
                    'admin.email_job_edit',
                ]),
                'name': 'Email',
            },
        ],
    }

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

admin_bp.add_url_rule(
    '/announcement',
    view_func = ListView.as_view(
        'announcement_list',
        template = 'admin/table.html',
        model_class = Announcement,
        pagination_getter = Announcement.pagination_getter,
        table = Table(
            description = NewAnnouncementForm.__doc__,
            columns = [
                Column(
                    attrname = 'title',
                    header = 'Title',
                ),
                Column(
                    attrname = 'is_active',
                    header = 'Active?',
                    cast = lambda announcement, value: yesno(value),
                ),
                Column(
                    attrname = 'human_datetime_range_html',
                    header = 'Range',
                ),
                Column(
                    attrname = 'message',
                    header = 'Message',
                ),
            ],
        )
    ),
)

admin_bp.add_url_rule(
    '/announcement/edit/<id>',
    view_func = EditObjectView.as_view(
        'announcement_edit',
        template = 'admin/edit_form.html',
        model_class = Announcement,
        form_class = EditAnnouncementForm,
        after_endpoint = '.announcement_list',
    ),
)

admin_bp.add_url_rule(
    '/announcement/new',
    view_func = EditObjectView.as_view(
        'announcement_new',
        template = 'admin/edit_form.html',
        model_class = Announcement,
        form_class = NewAnnouncementForm,
        after_endpoint = '.announcement_list',
    ),
)

admin_bp.add_url_rule(
    '/user',
    view_func = ListView.as_view(
        'user_list',
        template = 'admin/table.html',
        model_class = User,
        pagination_getter = User.pagination_getter,
        edit_endpoint = lambda user: url_for('.user_edit', id=user.id),
        new_endpoint = '.user_new',
        table = Table(
            description = Markup(
                '<p>User accounts.</p>'
                '<p>If active they may login to the site.</p>'
                '<p>If admin they may access these admin pages.</p>'
                '<p>Set "Reset Password" flag to force account to change password.</p>'
                '<p>Accounts can be related to an employee object to autofill the request form.</p>'
            ),
            columns = [
                Column(
                    attrname = 'email_address',
                    header = 'Email Address',
                    cast = many_formatter,
                    th_attrs = {
                        'data-tooltip': User.email_address.info.get('blurb'),
                    },
                ),
                Column(
                    attrname = 'email_verified_at',
                    header = 'Email Verified',
                    cast = many_formatter,
                    th_attrs = {
                        'data-tooltip': User.email_verified_at.info.get('blurb'),
                    },
                ),
                Column(
                    attrname = 'reset_password',
                    header = Markup(f'<span title="{User.reset_password.info['blurb']}">Reset Password?</span>'),
                    cast = many_formatter,
                    th_attrs = {
                        'data-tooltip': User.reset_password.info.get('blurb'),
                    },
                ),
                Column(
                    attrname = 'is_active',
                    header = Markup(f'<span title="{User.is_active.info['blurb']}">Active?</span>'),
                    cast = many_formatter,
                    th_attrs = {
                        'data-tooltip': User.is_active.info.get('blurb'),
                    },
                ),
                Column(
                    attrname = 'is_decider',
                    header = Markup(f'<span title="{User.is_decider.info['blurb']}">Decider?</span>'),
                    cast = many_formatter,
                    th_attrs = {
                        'data-tooltip': User.is_decider.info.get('blurb'),
                    },
                ),
                Column(
                    attrname = 'is_admin',
                    header = Markup(f'<span title="{User.is_admin.info['blurb']}">Admin?</span>'),
                    cast = many_formatter,
                    th_attrs = {
                        'data-tooltip': User.is_admin.info.get('blurb'),
                    },
                ),
                Column(
                    attrname = 'employee',
                    header = Markup(f'<span title="{User.employee.info['blurb']}">Employee</span>'),
                ),
            ],
        )
    ),
)

admin_bp.add_url_rule(
    '/user/<id>',
    view_func = EditObjectView.as_view(
        'user_edit',
        template = 'admin/edit_form.html',
        model_class = User,
        form_class = EditUserForm,
        after_endpoint = '.user_list',
    )
)

admin_bp.add_url_rule(
    '/user/new',
    view_func= NewObjectView.as_view(
        'user_new',
        template = 'admin/edit_form.html',
        model_class = User,
        form_class = NewUserForm,
        after_endpoint = '.user_list',
    )
)

admin_bp.add_url_rule(
    '/employee',
    view_func = ListView.as_view(
        'employee_list',
        template = 'admin/table.html',
        model_class = Employee,
        pagination_getter = Employee.pagination_getter,
        edit_endpoint = lambda obj: url_for('.employee_edit', id=obj.id),
        new_endpoint = '.employee_new',
        table = Table([
            Column(
                attrname = 'name',
                header = 'Name',
                cast = many_formatter,
            ),
            Column(
                attrname = 'employee_number',
                header = 'EE #',
                cast = many_formatter,
            ),
            Column(
                attrname = 'airline',
                header = 'Employer',
                cast = lambda employee, airline: airline.configured_display_code,
            ),
            Column(
                attrname = 'phone',
                header = 'Phone',
                cast = many_formatter,
            ),
            Column(
                attrname = 'user',
                header = 'User Account',
                cast = lambda employee, user: user.email_address if user else '',
            ),
        ])
    ),
)

admin_bp.add_url_rule(
    '/employee/<id>',
    view_func = EditObjectView.as_view(
        'employee_edit',
        template = 'admin/edit_form.html',
        model_class = Employee,
        form_class = EditEmployeeForm,
        after_endpoint = '.employee_list',
    )
)

admin_bp.add_url_rule(
    '/employee/new',
    view_func= NewObjectView.as_view(
        'employee_new',
        template = 'admin/edit_form.html',
        model_class = Employee,
        form_class = NewEmployeeForm,
        after_endpoint = '.employee_list',
    )
)

admin_bp.add_url_rule(
    '/jumpseat-request',
    view_func = ListView.as_view(
        'jumpseat_request_list',
        template = 'admin/table.html',
        model_class = JumpseatRequest,
        pagination_getter = JumpseatRequest.pagination_getter,
        edit_endpoint = lambda jumpseat_request: url_for('.jumpseat_request_edit', id=jumpseat_request.id),
        table = Table(
            description = JumpseatRequest.__doc__,
            columns = [
                Column(
                    attrname = 'flight_date',
                    header = 'Flight Date',
                    ),
                Column(
                    attrname = 'flight_number',
                    header = 'Flight #',
                    ),
                Column(
                    attrname = 'employee_airline.icao_code',
                    header = 'Flight #',
                    ),
                Column(
                    attrname = 'employee_number',
                    header = 'Empl. #',
                    ),
                Column(
                    attrname = 'employee_name',
                    header = 'Name',
                    ),
                Column(
                    attrname = 'request_by.email_address',
                    header = 'Requester Email',
                    ),
                Column(
                    attrname = 'status_html',
                    header = 'Status',
                    ),
            ]
        ),
    ),
)

admin_bp.add_url_rule(
    rule = '/jumpseat-request/<id>',
    view_func = EditObjectView.as_view(
        'jumpseat_request_edit',
        template = 'admin/edit_form.html',
        model_class = JumpseatRequest,
        form_class = EditJumpseatRequestForm,
        after_endpoint = '.jumpseat_request_list',
    ),
)

admin_bp.add_url_rule(
    rule = '/jumpseat-request/new',
    view_func = NewObjectView.as_view(
        'jumpseat_request_new',
        template = 'admin/edit_form.html',
        model_class = JumpseatRequest,
        form_class = NewJumpseatRequestForm,
        after_endpoint = '.jumpseat_request_list',
    ),
)

admin_bp.add_url_rule(
    rule = '/notification-rule',
    view_func = ListView.as_view(
        'notification_rule_list',
        model_class = NotificationRule,
        template = 'admin/table.html',
        pagination_getter = NotificationRule.pagination_getter,
        edit_endpoint = lambda obj: url_for('.notification_rule_edit', id=obj.id),
        table = Table(
            description = Markup("<p>A notification groups email address recipients to a notification event. This table exists to allow admins to edit the recipients list. Adding a new signal requires developer effort to make the signal and code to process it.</p>"),
            columns = [
                Column(
                    attrname = 'name',
                    header = 'Name',
                ),
                Column(
                    attrname = 'blurb',
                    header = 'Blurb',
                ),
                Column(
                    attrname = 'signal_name',
                    header = 'Signal Name',
                    th_attrs = {
                        'data-tooltip': NotificationRule.signal_name.info.get('blurb'),
                    },
                ),
                Column(
                    attrname = 'created_at_age_seconds',
                    header = 'Created At Seconds',
                    cast = lambda notification_rule, seconds: f'{seconds:,}' if seconds else '',
                    th_attrs = {
                        'data-tooltip': 'If given, the rule will only fire for jumpseat requests greater than or equal to this number of seconds.',
                    },
                ),
                Column(
                    attrname = 'recipients',
                    header = 'Recipients',
                    th_attrs = {
                        'data-tooltip': 'List of recipients for notificaiton rule.',
                    },
                    cast = lambda parent, recipient_list: unordered_list(map(lambda obj: obj.email_address, recipient_list))
                ),
            ],
         ),
    ),
)

admin_bp.add_url_rule(
    rule = '/email',
    view_func = ListView.as_view(
        'email_job_list',
        model_class = EmailJob,
        template = 'admin/table.html',
        edit_endpoint = lambda obj: url_for('.email_job_instance', id=obj.id),
        pagination_getter = EmailJob.pagination_getter,
        table = Table(
            description = EmailJob.__doc__,
            columns = [
                Column(
                    attrname = 'subject',
                    header = 'Subject',
                ),
                Column(
                    attrname = 'from_email_address',
                    header = 'From',
                ),
                Column(
                    attrname = 'recipients',
                    header = 'To',
                    cast = lambda email_job, recipients: unordered_list(map(mailto, recipients)),
                ),
                Column(
                    attrname = 'sent_at_formatted',
                    header = 'Sent',
                ),
            ]
        ),
    ),
)

admin_bp.add_url_rule(
    rule = '/email-job/<id>',
    view_func = SingleView.as_view(
        'email_job_instance',
        template = 'admin/email_job_instance.html',
        model_class = EmailJob,
    )
)

admin_bp.add_url_rule(
    rule = '/notification-rule/<id>',
    view_func = EditObjectView.as_view(
        'notification_rule_edit',
        template = 'admin/edit_form.html',
        model_class = NotificationRule,
        form_class = EditNotificationRuleForm,
        after_endpoint = '.notification_rule_list',
    ),
)

admin_bp.add_url_rule(
    rule = '/notification-rule/new',
    view_func = NewObjectView.as_view(
        'notification_rule_new',
        template = 'admin/edit_form.html',
        model_class = NotificationRule,
        form_class = EditNotificationRuleForm,
        after_endpoint = '.notification_rule_list',
    ),
)

# TODO
# - admin page for failed EmailJob objects.
