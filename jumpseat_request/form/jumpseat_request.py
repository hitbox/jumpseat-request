from flask import session
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import FieldList
from wtforms import FormField
from wtforms import HiddenField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Optional
from wtforms.validators import ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField

from jumpseat_request import settings
from jumpseat_request.extension import timezone
from jumpseat_request.form import EmployeeSubForm
from jumpseat_request.guest import get_current_user_or_create_guest
from jumpseat_request.model import Airline
from jumpseat_request.model import Employee
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import User
from jumpseat_request.model.user import password_hasher
from jumpseat_request.schema import JumpseatRequestDataSchema

jumpseat_request_data_schema = JumpseatRequestDataSchema()

def upper(x):
    if isinstance(x, str):
        x = x.upper()
    return x

def flight_date_field(label=None):
    return DateField(
        label = label,
        default = lambda: timezone.now().date(),
        validators = [
            DataRequired(),
        ],
        render_kw = {
            'placeholder': 'Flight Date',
        },
    )

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
        email_matches_current_user,
    ])
    field = StringField(**kwargs)
    return field


class JumpseatRequestSubform(FlaskForm):
    class Meta:
        csrf = False

    flight_date = flight_date_field()

    flight_number = flight_number_field()


class JumpseatRequestFormMixin:

    flight_date = flight_date_field()

    flight_number = flight_number_field()

    employee_airline = employee_airline_field()

    employee_number = StringField(
        label = 'Employee #',
        validators = [
            DataRequired(),
        ],
    )

    employee_name = StringField(
        label = 'Name',
        validators = [
            Optional(),
        ],
    )

    employee_email = employee_email_address_field()

    employee_phone = StringField(
        label = 'Phone',
        validators = [
            Optional(),
        ],
    )


class EditJumpseatRequestAdminForm(FlaskForm):

    flight_date = flight_date_field()

    flight_number = flight_number_field()

    employee_airline = employee_airline_field()

    employee_number = StringField(
        label = 'Employee #',
        validators = [
            DataRequired(),
        ],
    )

    employee_name = StringField(
        label = 'Name',
        validators = [
            Optional(),
        ],
    )

    # exclude requirement to match logged in user's email
    employee_email = StringField(
        label = 'Email',
        validators = [
            DataRequired(),
        ]
    )

    employee_phone = StringField(
        label = 'Phone',
        validators = [
            Optional(),
        ],
    )

    submit = SubmitField()


class EditJumpseatRequestForm(JumpseatRequestFormMixin, FlaskForm):

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
        render_kw = {
            'class': '',
            'role': 'button',
        }
    )

    deny = SubmitField(
        render_kw = {
            'class': 'secondary danger',
            'role': 'button',
        }
    )

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
