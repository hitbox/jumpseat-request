from flask_wtf import FlaskForm
from jumpseat_request.model import Employee
from jumpseat_request.model import User
from wtforms import BooleanField
from wtforms import FormField
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField

from .employee import EmployeeSubForm
from .mixin import OrderedFieldsMixin
from .mixin import OrderedFieldsMixin

def unique_email_address(form, field):
    email_address = field.data
    exists = User.get_unique_by_attribute(
        'email_address',
        email_address,
        case_sensitive=False,
    )
    if exists:
        raise ValidationError(f'Email address already exists {email_address!r}')

def reset_password_field(**kwargs):
    kwargs.setdefault('label', 'Reset Password?')
    kwargs.setdefault('render_kw', {
            'title': 'Account is required to change their password.',
            'role': 'switch',
        }
    )
    return BooleanField(**kwargs)

def is_decider_field(**kwargs):
    kwargs.setdefault('label', 'Decider?')
    kwargs.setdefault('render_kw', {
        'title': 'Account may approve and deny jump seat requests.',
        'role': 'switch',
    })
    return BooleanField(**kwargs)

def email_address_field(**kwargs):
    kwargs.setdefault('label', 'Email')
    kwargs.setdefault('validators', [
            DataRequired(),
        ]
    )
    return StringField(**kwargs)

def is_admin_field(**kwargs):
    kwargs.setdefault('label', 'Admin?')
    kwargs.setdefault('render_kw', {
            'title': 'If admin, user can access the admin pages.',
            'role': 'switch',
        }
    )
    return BooleanField(**kwargs)

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

    email_address = email_address_field()

    is_admin = is_admin_field()

    is_active = is_active_field()

    employee = employee_field()

    email_verified = BooleanField(
        'Email Verified?',
        render_kw = {
            'title': 'Check to mark email verified.',
            'role': 'switch',
        }
    )

    # Employee associated with methods of contacts.
    is_decider = is_decider_field()

    is_admin = is_admin_field()

    password_hash = PasswordField(
        label = 'Password',
        validators = [
            DataRequired()
        ],
    )

    confirm = confirm_password_field(
        label = 'Confirm Password',
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
            if field.name == 'email_verified' and field.data:
                obj.confirm_email()
            else:
                field.populate_obj(obj, field.name)


class EditAccountForm(OrderedFieldsMixin, FlaskForm):
    """
    User edit own account.
    """

    email_address = email_address_field()

    update = SubmitField()

    def populate_obj(self, user):
        super().populate_obj(user)
        user.verified_at = None


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

    email_address = email_address_field(
        validators = [
            DataRequired(),
            unique_email_address,
        ],
    )

    is_active = is_active_field()

    # Employee associated with methods of contacts.
    is_decider = is_decider_field()

    is_admin = is_admin_field()

    is_decider = is_decider_field()

    employee = employee_field()

    password_hash = PasswordField(
        'Password',
        validators = [
            DataRequired(),
        ],
    )

    confirm = confirm_password_field(label='Confirm Password')

    reset_password = reset_password_field()

    create = SubmitField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ChangePassword(FlaskForm):

    password_hash = PasswordField(
        label = 'New Password',
        validators = [
            DataRequired(),
        ],
    )

    confirm = confirm_password_field(
        label = 'Confirm Password',
    )

    update = SubmitField()


class RegisterUserForm(FlaskForm):
    """
    Register new user account.
    """

    email_address = email_address_field(
        validators = [
            DataRequired(),
            unique_email_address,
        ],
    )

    create = SubmitField()
