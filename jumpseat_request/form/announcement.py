from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import DateTimeField
from wtforms import FieldList
from wtforms import FormField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo
from wtforms.validators import optional
from wtforms_sqlalchemy.fields import QuerySelectField

from jumpseat_request.extension import db
from jumpseat_request.model import Employee
from jumpseat_request.model import Airline
from jumpseat_request.model import AnnouncementLevel
from jumpseat_request.model.user import password_hasher

def datetime_field():
    return DateTimeField(
        'Start',
        render_kw = {
            'title': 'Start datetime of announcement.',
        },
    )


class AnnouncementMixin(FlaskForm):
    """
    Edit announcement
    """

    is_active = BooleanField(
        'Active?',
        default = True,
        render_kw = {
            'title': 'Announcement is active.',
            'role': 'switch',
        },
    )

    title = StringField(
        render_kw = {
            'title': 'Title of message',
        },
    )

    level = QuerySelectField(
        query_factory = AnnouncementLevel.query_factory,
        get_label = 'name',
        allow_blank = False,
    )

    starts_at = DateTimeField(
        'Start',
        format = '%Y-%m-%d %H:%M',
        render_kw = {
            'title': 'Start datetime of announcement.',
        },
        validators = [
            optional(),
        ],
    )

    def validate_ends_at(form, field):
        starts = form.starts_at.data
        ends = form.ends_at.data

        if starts is None and ends is None:
            raise ValidationError(f'Start and end cannot both be empty.')

    ends_at = DateTimeField(
        'End',
        format = '%Y-%m-%d %H:%M',
        render_kw = {
            'title': 'End datetime of announcement.',
        },
        validators = [
            optional(),
            validate_ends_at,
        ],
    )

    message = StringField(
        render_kw = {
            'title': 'Body of message',
        },
    )


class EditAnnouncementForm(AnnouncementMixin):
    """
    Edit announcement--a message that is flashed to users.
    """

    update = SubmitField()


class NewAnnouncementForm(AnnouncementMixin):
    """
    New announcement--a message that is flashed to users.
    """

    create = SubmitField()
