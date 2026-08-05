import zoneinfo

from datetime import datetime
from datetime import time
from datetime import timedelta
from zoneinfo import ZoneInfo

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import DateTimeField
from wtforms import Form
from wtforms import FormField
from wtforms import HiddenField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional
from wtforms.validators import ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField

from jumpseat_request import settings
from jumpseat_request.extension import timezone
from jumpseat_request.model import Airline
from jumpseat_request.model import Employee
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import Rank
from jumpseat_request.model import User
from jumpseat_request.model.user import password_hasher

from .field import ISODateTimeField
from .field import switch_field

def upper(x):
    if isinstance(x, str):
        x = x.upper()
    return x

def flight_datetime_field(**kwargs):
    kwargs.setdefault('timespec', 'minutes')
    label = kwargs.setdefault('label', 'Flight Date')
    render_kw = kwargs.setdefault('render_kw', {})
    render_kw.setdefault('placeholder', 'Flight Date')
    kwargs.setdefault(
        'validators', [
            DataRequired(),
        ]
    )
    return ISODateTimeField(**kwargs)

def flight_number_field(label=None):
    return StringField(
        label = label,
        filters = [
            upper,
        ],
        validators = [
            DataRequired(),
        ],
        render_kw = {
            'placeholder': 'Flight Number',
        },
    )

def employee_airline_field(label=None):
    return QuerySelectField(
        label = label,
        query_factory = Airline.query_factory,
        get_label = 'icao_code',
        allow_blank = False,
    )

def email_matches_current_user(form, field):
    if current_user.is_authenticated and current_user.email_address != field.data:
        raise ValidationError(
            f'Employee email address does not match logged in user.'
        )

def employee_email_address_field(**kwargs):
    kwargs.setdefault('label', 'Email')
    kwargs.setdefault('validators', [
        DataRequired(),
    ])
    field = StringField(**kwargs)
    return field


class JumpseatRequestSubform(FlaskForm):
    class Meta:
        csrf = False

    flight_number = flight_number_field()

    flight_datetime = flight_datetime_field(
        label = 'Flight Date',
    )


class JumpseatRequestFormMixin:

    flight_number = flight_number_field()

    flight_datetime = flight_datetime_field(
        label = 'Flight Date',
    )

    scheduled_departure_airport = StringField(
        label = 'Departure',
        validators = [
            Length(min=3, max=3),
        ],
        render_kw = {
            'placeholder': 'Sched. Departure Airport',
        },
    )

    scheduled_arrival_airport = StringField(
        label = 'Arrival',
        validators = [
            Length(min=3, max=3),
        ],
        render_kw = {
            'placeholder': 'Sched. Arrival Airport',
        },
    )

    rank_object = QuerySelectField(
        label = 'Rank',
        query_factory = Rank.query_factory,
        get_label = lambda obj: f'{obj.name}({obj.code})',
        allow_blank = True,
    )

    employee_airline = employee_airline_field()

    employee_number = StringField(
        label = 'Employee #',
        validators = [
            DataRequired(),
        ],
        render_kw = {
            'placeholder': 'Required Employee Number',
        },
    )

    employee_name = StringField(
        label = 'Name',
        validators = [
            DataRequired(),
        ],
        render_kw = {
            'placeholder': 'Employee Name',
        },
    )

    employee_email = employee_email_address_field()

    employee_phone = StringField(
        label = 'Phone',
        validators = [
            Optional(),
        ],
        render_kw = {
            'placeholder': 'Employee Phone',
        },
    )


class EditJumpseatRequestAdminForm(JumpseatRequestFormMixin, FlaskForm):

    save = SubmitField()


class EditJumpseatRequestForm(JumpseatRequestFormMixin, FlaskForm):

    save_employee_info = switch_field(
        label = 'Save Employee Info?',
        render_kw = {
            'placeholder': 'Save Employee Information?',
        },
    )

    submit = SubmitField()


class JumpseatRequestActionForm(FlaskForm):
    """
    Approve or deny a jumpseat request with optional reason.
    """

    id = HiddenField()

    reason = TextAreaField(
        validators = [
            Optional()
        ],
        render_kw = {
            'placeholder': 'Optional Decision Reason',
        }
    )

    approve = SubmitField(
        label = 'Approve',
        render_kw = {
            'class': '',
            'role': 'button',
        }
    )

    deny = SubmitField(
        label = 'Deny',
        render_kw = {
            'class': 'secondary',
            'role': 'button',
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'obj' in kwargs:
            jumpseat_request = kwargs['obj']
        if jumpseat_request and not jumpseat_request.is_undecided():
            del self.approve
            del self.deny

    def populate_obj(form, jumpseat_request):
        """
        Update JumpseatRequest object calling special methods for approving and
        denying.
        """
        # Calling super().populate_obj will overwrite our approve/deny methods
        # with this form's fields.
        # Update like normal excluding two buttons which would overwrite the
        # methods on the instance.
        exclude = {'approve', 'deny'}
        for field in form:
            if field.name not in exclude:
                field.populate_obj(jumpseat_request, field.name)

        # Call related model methods for buttons.
        if form.approve.data:
            jumpseat_request.approve()
        elif form.deny.data:
            jumpseat_request.deny()


class NewJumpseatRequestForm(JumpseatRequestFormMixin, FlaskForm):
    """
    Create a new jumpseat request.
    """

    create = SubmitField()


def timezone_choices(keys=None):
    choices = []

    timezones = [
        'America/New_York',
        'UTC'
    ]

    def sort_key(timezone_key):
        if timezone_key in timezones:
            return timezones.index(timezone_key)
        else:
            return 999

    keys = (key for key in zoneinfo.available_timezones() if key in timezones)
    keys = sorted(keys, key=sort_key)
    for key in keys:
        choice = (key, f'{datetime.now(ZoneInfo(key)).tzname()} ({key})')
        choices.append(choice)
    return choices

def today_noon():
    # use extension for timezone
    today = timezone.today()
    today_noon = datetime.combine(today, time(12,0), tzinfo=timezone.zoneinfo)
    return today_noon

def tomorrow_midnight():
    # use extension for timezone
    tomorrow = timezone.now() + timedelta(days=1)
    tomorrow_midnight = tomorrow.replace(
        hour = 0,
        minute = 0,
        microsecond = 0,
        tzinfo = timezone.zoneinfo,
    )
    return tomorrow_midnight

class SelectFlightDatetimeForm(Form):

    timezone = SelectField(
        choices = timezone_choices(),
        default = 'America/New_York',
    )

    start = ISODateTimeField(
        label = 'Flight datetime start',
        timespec = 'minutes',
        validators = [
            DataRequired()
        ],
    )

    end = ISODateTimeField(
        label = 'Flight datetime end',
        timespec = 'minutes',
        validators = [
            DataRequired()
        ],
    )

    select = SubmitField()

    export_excel = SubmitField(
        render_kw = {
            'class': 'secondary',
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.start.data is None:
            self.start.data = today_noon()

        if self.end.data is None:
            self.end.data = tomorrow_midnight()
