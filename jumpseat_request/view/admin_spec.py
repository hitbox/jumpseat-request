from dataclasses import dataclass
from dataclasses import field
from typing import Optional

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.views import View
from flask_login import current_user
from flask_wtf import FlaskForm
from markupsafe import Markup

from htmlkit.lists import unordered_list
from htmlkit.table import Column
from htmlkit.table import Table
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
from jumpseat_request.model.admin_spec import AdminSpec
from jumpseat_request.seed import seed_database
from jumpseat_request.view.pluggable import EditObjectView
from jumpseat_request.view.pluggable import ListView
from jumpseat_request.view.pluggable import NewObjectView

admin_specs_for_views = [
    AdminSpec(
        view_class = ListView,
        pagination_getter = Announcement.pagination_getter,
        model_class = Announcement,
        edit_form = EditAnnouncementForm,
        new_form = NewAnnouncementForm,
        html_table = Table(
            description = Announcement.__doc__,
            columns = [
                Column(
                    attrname = 'is_active',
                    header = 'Active?',
                ),
                Column(
                    attrname = 'starts_at',
                    header = 'Start',
                ),
                Column(
                    attrname = 'ends_at',
                    header = 'End',
                ),
                Column(
                    attrname = 'level',
                    header = 'Level',
               )
            ],
        ),
    ),
    AdminSpec(
        view_class = ListView,
        pagination_getter = User.pagination_getter,
        model_class = User,
        edit_form = EditUserForm,
        new_form = NewUserForm,
        html_table = Table(
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
    ),
    AdminSpec(
        view_class = ListView,
        pagination_getter = Employee.pagination_getter,
        model_class = Employee,
        edit_form = EditEmployeeForm,
        new_form = NewEmployeeForm,
        html_table = Table([
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
    AdminSpec(
        view_class = ListView,
        model_class = NotificationRule,
        pagination_getter = NotificationRule.pagination_getter,
        edit_form = EditNotificationRuleForm,
        html_table = None,
     ),
    AdminSpec(
        view_class = ListView,
        pagination_getter = NotificationRule.pagination_getter,
        model_class = JumpseatRequestNotificationRuleAssoc,
        html_table = Table(
            description = JumpseatRequestNotificationRuleAssoc.__doc__,
            columns = [
                Column(
                    attrname = 'jumpseat_request',
                ),
                Column(
                    attrname = 'notification_rule',
                ),
                Column(
                    attrname = 'message',
                ),
            ],
        ),
    ),
    AdminSpec(
        view_class = ListView,
        model_class = ApplicationSetting,
        pagination_getter = ApplicationSetting.pagination_getter,
        edit_view_class = EditObjectView,
        edit_endpoint = lambda instance: url_for('application_setting_edit', id=instance.id),
        edit_form = ApplicationSetting.get_settings_form,
        edit_rule = '/application-setting/<name>',
        after_endpoint = 'application_setting_list',
        # special way to populate these forms:
        edit_kwargs_for_form = lambda: { 'data': ApplicationSetting.as_data() },
        html_table = Table(
            columns = [
                Column(
                    attrname = 'name',
                ),
                Column(
                    attrname = 'value',
                ),
            ],
        ),
    ),
]
