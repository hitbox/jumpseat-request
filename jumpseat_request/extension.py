from uuid import UUID

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_message = 'Login'
login_manager.login_view = 'login.user_account'

@login_manager.user_loader
def user_loader(user_id):
    from jumpseat_request.model import User
    user_id = UUID(user_id)
    return db.session.get(User, user_id)

def init_app(app):
    db.init_app(app)
    login_manager.init_app(app)
