from functools import wraps

from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user

def login_and_password_ok(view_func):
    """
    Decorate view to require login and redirect to force password reset.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        is_authenticated = getattr(current_user, 'is_authenticated', False)
        if not is_authenticated:
            flash('Login required', 'danger')
            return redirect(url_for('auth.login', next=request.url))

        reset_password = getattr(current_user, 'reset_password', False)
        if reset_password:
            # Redirect to force password change.
            flash('Change password required', 'warning')
            url = url_for(
                'auth.change_password',
                user_id = current_user.id,
                next = request.url,
            )
            return redirect(url)

        return view_func(*args, **kwargs)

    return wrapper
