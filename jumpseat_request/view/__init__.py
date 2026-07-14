from .admin import admin_bp
from .app_settings import app_settings_bp
from .auth import auth_bp
from .email_verification import email_verification_bp
from .employee import employee_bp
from .jumpseat_request import jumpseat_request_bp
from .notification import notification_bp
from .user import user_bp

def init_app(app):
    app.register_blueprint(admin_bp)
    app.register_blueprint(app_settings_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(email_verification_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(jumpseat_request_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(user_bp)
