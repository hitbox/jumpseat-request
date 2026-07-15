from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField

from jumpseat_request.extension import db
from jumpseat_request.model import Employee
from jumpseat_request.model import User
from jumpseat_request.model.user import password_hasher

from .mixin import OrderedFieldsMixin

def reset_password_field():
    return BooleanField(
        'Reset Password?',
        render_kw = {
            'title': 'Account is required to change their password.',
            'role': 'switch',
        },
    )

def is_decider_field(**kwargs):
    kwargs.setdefault('label', 'Approver?')
    kwargs.setdefault('render_kw', {
        'title': 'Account may approve and deny jump seat requests.',
        'role': 'switch',
    })
    return BooleanField(**kwargs)

def email_address_field():
    return StringField(
        'Email',
        validators = [
            DataRequired(),
        ],
    )

def is_admin_field():
    return BooleanField(
        label='Admin?',
        render_kw = {
            'title': 'If admin, user can access the admin pages.',
            'role': 'switch',
        },
    )

def is_active_field(**kwargs):
    kwargs.setdefault('label', 'Active?')
    kwargs.setdefault('default', True)
    kwargs.setdefault('render_kw', {
        'title': 'If active this account can be used to log in.',
        'role': 'switch',
    })
    return BooleanField(**kwargs)

def employee_field(**kwargs):
    kwargs.setdefault('query_factory', Employee.query_factory)
    kwargs.setdefault('get_label', 'name')
    kwargs.setdefault('allow_blank', True)
    return QuerySelectField(**kwargs)

def confirm_password_field(**kwargs):
    # Must have a "password_hash" field on the form.
    kwargs.setdefault('label', None)
    kwargs.setdefault('validators', )
    return PasswordField(**kwargs)


class EditUserForm(FlaskForm):
    """
    Edit user account.
    """

    __fields__ = [
        'id',
        'email_address',
        'employee',
        'is_admin',
        'is_active',
    ]

    email_address = email_address_field()

    is_admin = is_admin_field()

    is_active = is_active_field()

    employee = employee_field()

    # Employee associated with methods of contacts.
    is_decider = is_decider_field()

    is_admin = is_admin_field()

    email_verified = BooleanField(
        'Email Verified?',
        render_kw = {
            'title': 'Check to mark email verified.',
            'role': 'switch',
        }
    )

    reset_password = reset_password_field()

    update = SubmitField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_admin.data:
            # Add "dangerous" class when is_admin is True.
            kwargs = self.is_admin.render_kw or {}
            kwargs.update({
                'class': 'danger',
            })
            self.is_admin.render_kw = kwargs

    def populate_obj(self, obj):
        for field in self:
            if field.name == 'email_verified':
                obj.confirm_email()
            else:
                field.populate_obj(obj, field.name)


class EditAccountForm(OrderedFieldsMixin, FlaskForm):
    """
    User edit own account.
    """

    email_address = email_address_field()

    update = SubmitField()


class NewUserForm(FlaskForm):
    """
    Admin form to create a new user.
    """

    __fields__ = [
        'email_address',
        'employee',
        'is_admin',
        'is_active',
        'is_decider',
    ]

    email_address = email_address_field()

    is_active = is_active_field()

    # Employee associated with methods of contacts.
    is_decider = is_decider_field()

    is_admin = is_admin_field()

    is_decider = is_decider_field()

    employee = employee_field()

    password_hash = PasswordField(
        'Password',
        validators = [DataRequired()],
    )

    confirm = confirm_password_field(label='Confirm Password')

    login = SubmitField()


class ChangePassword(FlaskForm):

    password_hash = PasswordField(
        'New Password',
        validators = [DataRequired()],
    )

    confirm = confirm_password_field(label='Confirm Password')

    update = SubmitField()
