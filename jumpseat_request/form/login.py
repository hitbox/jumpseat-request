from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):

    email_address = StringField(
        validators = [
            DataRequired(),
        ],
    )

    password = PasswordField(
        validators = [
            DataRequired(),
        ],
    )

    next_ = HiddenField()
    
    login = SubmitField()
