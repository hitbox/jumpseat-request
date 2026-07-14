from flask_wtf import FlaskForm
from wtforms import DateTimeField
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField

from jumpseat_request.model import User

def user_field():
    return QuerySelectField(
        query_factory = User.query_factory,
        get_label = 'email_address',
        allow_blank = True,
    )


class EmailVerificationFormMixin:

    confirm_hash = StringField(
        validators = [
            DataRequired()
        ],
    )

class ConfirmHashEmailVerificationForm(FlaskForm):
    """
    Confirm email verification from secret hash.
    """

    user = user_field()

    confirm_secret = StringField(
        validators = [
            DataRequired()
        ],
    )

    confirm = SubmitField()

    def populate_obj(self, email_verification):
        secret = self.confirm_secret.data
        if email_verification.check_confirm_hash(secret):
            email_verification.confirm_verification()


class EditEmailVerificationForm(FlaskForm):
    """
    Edit an email verification for a user.
    """

    user = QuerySelectField(
        query_factory = User.query_factory,
        get_label = 'email_address',
        allow_blank = True,
    )

    expire_at = DateTimeField()

    confirm_hash = StringField(
        'Secret',
        validators = [
            DataRequired()
        ],
    )

    update = SubmitField()


class NewEmailVerificationForm(FlaskForm):
    """
    Create a new email verification for a user.
    """

    user = user_field()

    confirm_hash = StringField(
        'Secret',
        validators = [
            DataRequired()
        ],
    )

    save = SubmitField()
