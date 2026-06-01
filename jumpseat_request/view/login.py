from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_user

from jumpseat_request.extension import login_manager
from jumpseat_request.form import LoginForm
from jumpseat_request.model import User

login_bp = Blueprint('login', __name__, url_prefix='/login')

@login_bp.route('/user', methods=['GET', 'POST'])
def user_account():
    """
    Login with app user account.
    """
    login_form = LoginForm(request.form)

    if request.method == 'GET':
        login_form.next_.data = request.args.get('next')

    elif request.method == 'POST':
        if login_form.validate():
            user = User.by_username(login_form.username.data)
            if user is not None:
                if user.check_password(login_form.password.data):
                    login_user(user, remember=True)
                    flash('Logged in', 'success')
                    next_url = (
                        login_form.next_.data
                        or url_for('jumpseat.list_requests')
                    )
                    return redirect(next_url)
                else:
                    flash('Invalid username or password', 'danger')

    context = {
        'login_form': login_form,
    }
    return render_template('login.html', **context)
