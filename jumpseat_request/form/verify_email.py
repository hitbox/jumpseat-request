from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms import BooleanField
from wtforms import Form
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

class VerifyEmailForm(FlaskForm):
    """
    Send email verification email.
    """

    email_address = StringField(
        'Email',
        validators = [
            DataRequired(),
        ],
    )

    send = SubmitField()
