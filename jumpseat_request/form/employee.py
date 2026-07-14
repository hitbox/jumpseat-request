from flask import session
from flask_wtf import FlaskForm
from wtforms import FieldList
from wtforms import FormField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField

from jumpseat_request.extension import db
from jumpseat_request.model import Airline
from jumpseat_request.model import Employee
from jumpseat_request.model import User
from jumpseat_request.model.user import password_hasher
from jumpseat_request.settings import AirlineLabelGetter

from .mixin import OrderedFieldsMixin

def user_select_field():
    return QuerySelectField(
        query_factory = User.query_factory,
        get_label = 'email_address',
        allow_blank = True,
        render_kw = {
            'title': Employee.user.info.get('blurb', ''),
        }
    )


def strip_string(x):
    if isinstance(x, str):
        return x.strip()
    else:
        return x

class EmployeeFormMixin:
    """
    Mixin common form fields for Employee objects.
    """

    airline = QuerySelectField(
        query_factory = Airline.query_factory,
        get_label = AirlineLabelGetter(),
        allow_blank = True,
        render_kw = {
            'title': Employee.airline.info.get('blurb', '')
        }
    )

    name = StringField(
        render_kw = {
            'title': Employee.name.info.get('blurb', ''),
        },
    )

    phone = StringField()

    employee_number = StringField(
        validators = [
            DataRequired(),
        ],
        render_kw = {
            'title': Employee.employee_number.info.get('blurb', ''),
        },
    )

    user = user_select_field()


class NewEmployeeForm(FlaskForm, EmployeeFormMixin):
    """
    Create a new Employee object.
    """

    create = SubmitField()


class EmployeeSubForm(FlaskForm):
    """
    Employee information
    """

    class Meta:
        # disable CSRF for sub-form.
        csrf = False


    airline = QuerySelectField(
        label = 'Employer',
        query_factory = Airline.query_factory,
        get_label = AirlineLabelGetter(),
        get_pk = lambda airline: str(airline.id),
        validators = [
            DataRequired(),
        ],
    )

    employee_number = StringField(
        validators = [
            DataRequired(),
        ],
        render_kw = {
            'placeholder': 'Employee Number',
        },
    )

    name = StringField(
        filters = [
            strip_string,
        ],
        render_kw = {
            'placeholder': 'Optional Employee Name',
        },
    )

    email_address = StringField(
        'Email',
        validators = [
            DataRequired(),
        ],
    )

    phone = StringField(
        validators = [
            DataRequired(),
        ],
    )


class EditEmployeeForm(FlaskForm, EmployeeFormMixin):
    """
    Edit an Employee object.
    """

    update = SubmitField()
