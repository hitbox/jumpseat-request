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
from jumpseat_request.form import EditJumpseatRequestAdminForm
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

admin_specs_for_views = [
    {
        'model_class': Announcement,
        'edit_form': EditAnnouncementForm,
        'new_form': NewAnnouncementForm,
        'html_table': Table(
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
        ),
    },
    {
        'model_class': User,
        'edit_form': EditUserForm,
        'new_form': NewUserForm,
        'html_table': Table(
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
                    header = 'Email',
                    cast = many_formatter,
                ),
                Column(
                    attrname = 'email_verified_at',
                    header = 'Email Verified',
                    cast = many_formatter,
                ),
                Column(
                    attrname = 'reset_password',
                    header = Markup(f'<span title="{User.reset_password.info['blurb']}">Reset Password?</span>'),
                    cast = many_formatter,
                ),
                Column(
                    attrname = 'is_active',
                    header = Markup(f'<span title="{User.is_active.info['blurb']}">Active?</span>'),
                    cast = many_formatter,
                ),
                Column(
                    attrname = 'is_decider',
                    header = Markup(f'<span title="{User.is_decider.info['blurb']}">Decider?</span>'),
                    cast = many_formatter,
                ),
                Column(
                    attrname = 'is_admin',
                    header = Markup(f'<span title="{User.is_admin.info['blurb']}">Admin?</span>'),
                    cast = many_formatter,
                ),
                Column(
                    attrname = 'employee',
                    header = Markup(f'<span title="{User.employee.info['blurb']}">Employee</span>'),
                ),
            ],
        )
    },
    {
        'model_class': Employee,
        'edit_form': EditEmployeeForm,
        'new_form': NewEmployeeForm,
        'html_table': Table([
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
    },
    {
        'model_class': JumpseatRequest,
        'edit_form': EditJumpseatRequestAdminForm,
        'new_form': NewJumpseatRequestForm,
        'html_table': Table([
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
        ]),
    },
    {
        'model_class': NotificationRule,
        'edit_form': EditNotificationRuleForm,
        'html_table': Table(
            description = "A notification groups email address recipients to a notification event. This table exists to allow admins to edit the recipients list. Adding a new signal requires developer effort to make the signal and code to process it.",
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
                ),
                Column(
                    attrname = 'created_at_age_seconds',
                    header = 'Created At Seconds',
                    cast = lambda notification_rule, seconds: f'{seconds:,}' if seconds else '',
                ),
                Column(
                    attrname = 'recipients',
                    cast = lambda parent, recipient_list: unordered_list(map(lambda obj: obj.email_address, recipient_list))
                ),
            ],
        ),
    },
    {
        'model_class': JumpseatRequestNotificationRuleAssoc,
        'html_table': Table([
            Column(
                attrname = 'jumpseat_request',
            ),
            Column(
                attrname = 'notification_rule',
            ),
            Column(
                attrname = 'message',
            ),
        ]),
    },
    {
        'model_class': ApplicationSetting,
        'edit_form': ApplicationSetting.get_settings_form,
        'pkname': 'name',
        'html_table': Table([
            Column(
                attrname = 'name',
            ),
            Column(
                attrname = 'value',
            ),
        ]),
    },
]

