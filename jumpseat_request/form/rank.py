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
from wtforms.validators import Optional
from wtforms_sqlalchemy.fields import QuerySelectField

from jumpseat_request.model import Rank

from .field import delete_submit_field

class EditRankForm(FlaskForm):
    """
    Edit rank object.
    """

    code = StringField(
        validators = [
            DataRequired(),
        ],
    )

    name = StringField(
        validators = [
            Optional(),
        ],
    )

    save = SubmitField()

    delete = delete_submit_field()


class NewRankForm(FlaskForm):
    """
    Create new rank object.
    """

    code = StringField(
        validators = [
            DataRequired(),
        ],
    )

    name = StringField(
        validators = [
            Optional(),
        ],
    )

    create = SubmitField()
