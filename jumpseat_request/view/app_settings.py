from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user

from jumpseat_request.extension import db
from jumpseat_request.extension import login_manager
from jumpseat_request.model import ApplicationSetting

app_settings_bp = Blueprint('app_settings', __name__, url_prefix='/settings')

@app_settings_bp.before_request
def require_admin_login():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin login required for initial app setup.', 'danger')
        return redirect(url_for(login_manager.login_view, next=request.url))

@app_settings_bp.route('/', methods=['GET', 'POST'])
def edit_required_settings():
    """
    Force user to input application settings until all are available.
    """
    form_class = ApplicationSetting.missing_settings_form()
    form = form_class()
    if form:
        flash(f'Application configuration neeeded.', 'danger')
        if form.validate_on_submit():
            form.populate_obj(None)
            db.session.commit()
            flash('Application settings updated', 'info')
            return redirect(url_for('root'))

        context = {
            'form': form,
        }
        return render_template('edit_form.html', **context)
    else:
        return redirect(url_for('root'))
