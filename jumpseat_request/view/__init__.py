from .admin import admin_bp
from .jumpseat_request import jumpseat_request_bp
from .login import login_bp
from .pluggable import TableEditor
from .user import user_bp

def init_app(app):
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(jumpseat_request_bp)
    return
