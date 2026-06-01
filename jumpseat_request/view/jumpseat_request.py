from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user

from jumpseat_request.extension import db
from jumpseat_request.extension import login_manager
from jumpseat_request.form import LoginForm
from jumpseat_request.model import JumpseatRequest

jumpseat_request_bp = Blueprint('jumpseat', __name__, url_prefix='/jumpseat')

@jumpseat_request_bp.before_request
def require_login():
    if not current_user.is_authenticated:
        flash('Login first to access jumpseat requests.', 'info')
        return redirect(url_for(login_manager.login_view, next=request.full_path))

@jumpseat_request_bp.route('/')
def list_requests():
    """
    List all jump seat requests.
    """

    jumpseat_requests = db.session.scalars(db.select(JumpseatRequest)).all()

    context = {
        'jumpseat_requests': jumpseat_requests,
    }

    return render_template('list_requests.html', **context)
