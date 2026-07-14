import click

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user

from jumpseat_request.extension import db
from jumpseat_request.extension import login_manager
from jumpseat_request.form import LoginForm
from jumpseat_request.model import Airline
from jumpseat_request.model import Employee
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import User
from jumpseat_request.settings import AirlineLabelGetter

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

class ModelChoice(click.ParamType):
    """
    Click paramater option with choices from datbase.
    """

    name = 'model_choice'

    def __init__(self, query_factory, value_getter=None):
        self.query_factory = query_factory
        self.value_getter = value_getter

    def convert(self, value, param, context):
        choices = self.query_factory()
        match = next((c for c in choices if self.value_getter(c) == value), None)
        if match is None:
            self.fail(
                f'{value!r} is not a valid choice.'
                f' Valid choices: {list(self.value_getter(c) for c in choices)}',
                param,
                context,
            )
        return match


@employee_bp.cli.command('create')
@click.option(
    '--airline',
    type = ModelChoice(
        query_factory = Airline.query_factory,
        value_getter = AirlineLabelGetter(),
    ),
    help = 'Employee\'s airline',
)
@click.option('--employee-number')
@click.option('--name')
@click.option('--phone')
@click.option(
    '--user',
    type = ModelChoice(
        query_factory = User.query_factory,
        value_getter = lambda user: user.email_address,
    ),
    help = 'User account by email to associate with employee record.',
)
def create(airline, employee_number, name, phone, user):
    """
    Create a new employee object.
    """
    employee = Employee(
        airline = airline,
        employee_number = employee_number,
        name = name,
        user = user,
        phone = phone,
    )
    db.session.add(employee)
    db.session.commit()
