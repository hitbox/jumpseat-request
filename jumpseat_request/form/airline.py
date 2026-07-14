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

from jumpseat_request.extension import db
from jumpseat_request.model import Employee
from jumpseat_request.model import Airline
from jumpseat_request.model.user import password_hasher

class EditAirlineForm(Form):
    """
    Edit user account.
    """
    iata_code = StringField()
    icao_code = StringField()
    update = SubmitField()


class NewAirlineForm(Form):
    """
    Create a new user.
    """

    iata_code = StringField()
    icao_code = StringField()
    save = SubmitField()
