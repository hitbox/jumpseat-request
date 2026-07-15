from flask_wtf import FlaskForm
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

from jumpseat_request.extension import db
from jumpseat_request.model import Employee
from jumpseat_request.model import User
from jumpseat_request.model.user import password_hasher

from .mixin import OrderedFieldsMixin
from .employee import EmployeeSubForm

def unique_email_address(form, field):
    email_address = field.data
    exists = User.get_unique_by_attribute(
        'email_address',
        email_address,
        case_sensitive=False,
    )
    if exists:
        raise ValidationError(f'Email address already exists {email_address!r}')

class RegisterUserForm(OrderedFieldsMixin, FlaskForm):
    """
    Register new user account.
    """

    employee = FormField(
        EmployeeSubForm
    )

    create = SubmitField()
