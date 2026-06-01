from wtforms import Form
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField

class LoginForm(Form):

    username = StringField()
    password = PasswordField()

    next_ = HiddenField()
    
    login = SubmitField()
