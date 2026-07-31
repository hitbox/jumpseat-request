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
    Edit Airline object.
    """
    iata_code = StringField(
        validators = [
            DataRequired()
        ],
    )

    icao_code = StringField(
        validators = [
            DataRequired()
        ],
    )

    update = SubmitField()


class NewAirlineForm(FlaskForm):
    """
    Create a new Airline object.
    """

    iata_code = StringField(
        validators = [
            DataRequired()
        ],
    )

    icao_code = StringField(
        validators = [
            DataRequired()
        ],
    )

    save = SubmitField()
