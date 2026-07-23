import click

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user

from jumpseat_request.click_choice import ModelChoice
from jumpseat_request.extension import db
from jumpseat_request.extension import login_manager
from jumpseat_request.form import LoginForm
from jumpseat_request.model import Airline
from jumpseat_request.model import Employee
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import User
from jumpseat_request.settings import AirlineLabelGetter

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

@employee_bp.cli.command('create')
@click.option(
    '--airline',
    type = ModelChoice(
        query_factory = Airline.query_factory,
        value_getter = lambda airline: airline.icao_code.casefold(),
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
        value_getter = lambda user: user.email_address.casefold(),
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
