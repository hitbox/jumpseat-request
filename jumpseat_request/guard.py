from functools import wraps

from flask import current_app
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user

change_password_endpoint = 'auth.change_password'

def response_for_reset_password():
    reset_password = getattr(current_user, 'reset_password', False)
    if reset_password:
        # Redirect to force password change.
        flash('Change password required', 'warning')
        url = url_for(
            change_password_endpoint,
            user_id = current_user.id,
            next = request.url,
        )
        return redirect(url)

def response_for_login_and_password_reset():
    is_authenticated = getattr(current_user, 'is_authenticated', False)
    if not is_authenticated:
        flash('Login required', 'danger')
        return redirect(url_for('auth.login', next=request.url))

    response = response_for_reset_password()
    if response:
        return response

def require_password_ok(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        reset_password = getattr(current_user, 'reset_password', False)
        if reset_password:
            flash('Must change password.', 'danger')
            url = url_for(
                change_password_endpoint,
                user_id = current_user.id,
                next = request.url,
            )
            return redirect(url)

        return view_func(*args, **kwargs)

    return wrapper

def login_and_password_ok(view_func):
    """
    Decorate view to require login and redirect to force password reset.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        response = response_for_login_and_password_reset()
        if response:
            return response

        return view_func(*args, **kwargs)

    return wrapper

def require_is_decider(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not getattr(current_user, 'is_decider', False):
            abort(
                403,
                description = f'Account {current_user.email_address} does'
                    ' not have permission to decide requests.'
            )
        return func(*args, **kwargs)
    return wrapped
