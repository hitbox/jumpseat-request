from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo

class EditAirlineForm(FlaskForm):
    """
    Edit user account.
    """
    iata_code = StringField()
    icao_code = StringField()
    update = SubmitField()


class NewAirlineForm(FlaskForm):
    """
    Create a new user.
    """

    iata_code = StringField()
    icao_code = StringField()
    save = SubmitField()
