from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from jumpseat_request import settings
from jumpseat_request.extension import db
from jumpseat_request.extension import login_manager
from jumpseat_request.form import ChangePassword
from jumpseat_request.form import LoginForm
from jumpseat_request.model import User

auth_bp = Blueprint('auth', __name__, url_prefix='/login')

@auth_bp.route('/user', methods=['GET', 'POST'])
def login():
    """
    Login with app user account.
    """
    login_form = LoginForm(request.form)

    if request.method == 'GET':
        login_form.next_.data = request.args.get('next')

    elif login_form.validate_on_submit():
        user = User.by_email(login_form.email_address.data)
        if user is not None:
            if user.check_password(login_form.password.data):
                login_user(user, remember=True)
                flash(f'Logged in', 'success')
                next_url = (
                    login_form.next_.data
                    or request.args.get('next')
                    or url_for('jumpseat_request.landing_page')
                )
                return redirect(next_url)
            else:
                flash('Invalid email or password', 'danger')

    context = {
        'login_form': login_form,
    }
    return render_template('login.html', **context)

@auth_bp.route('/callback', methods=['GET', 'POST'])
def callback():
    pass

@auth_bp.route('/change-password/<user_id>', methods=['GET', 'POST'])
def change_password(user_id):
    """
    Allow or force user to change thier password.
    """
    user = db.session.get(User, {'id': user_id})

    form = ChangePassword()

    if form.validate_on_submit():
        login_user(user, remember=True)
        form.populate_obj(user)
        user.reset_password = False
        db.session.commit()
        flash('Password changed', 'success')
        url = request.args.get('next', url_for(settings.default_endpoint()))
        return redirect(url)

    context = {
        'form': form,
    }

    return render_template('form.html', **context)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f'Logged out', 'success')
    return redirect(url_for('root'))
