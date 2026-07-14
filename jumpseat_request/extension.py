from uuid import UUID

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_verify import TimedToken

from flask_timezone import TimeZone
from flask_smtp import SMTP

db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_message = 'Login'
login_manager.login_view = 'auth.login'
email_verify = TimedToken()

timezone = TimeZone()

smtp = SMTP()

@login_manager.user_loader
def user_loader(user_id):
    from jumpseat_request.model import User
    user_id = UUID(user_id)
    return db.session.get(User, user_id)

def init_app(app):
    db.init_app(app)
    email_verify.init_app(app)
    login_manager.init_app(app)
    smtp.init_app(app)
    timezone.init_app(app)
