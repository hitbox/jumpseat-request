from flask import Flask
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session as flask_session
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired

from . import extension
from . import tasks
from . import template_filter
from . import view
from .extension import db
from .extension import timezone
from .middleware import PrefixMiddleware
from .model import Announcement
from .model import ApplicationSetting

def create_app():
    app = Flask(__name__)

    app.config.from_envvar('JUMPSEAT_REQUEST_CONFIG')

    PrefixMiddleware.init_app(app)
    extension.init_app(app)
    view.init_app(app)
    tasks.init_app(app)
    template_filter.init_app(app)

    nice_handle_exception = app.config.get('NICE_HANDLE_EXCEPTIONS', False)

    if nice_handle_exception:
        @app.errorhandler(Exception)
        def handle_exception(e):
            return render_template('exception.html', e=e)

    @app.route('/')
    def root():
        """
        Redirect to landing page for root.
        """
        return redirect(url_for('jumpseat_request.landing_page'))

    @app.route('/messages')
    def messsages():
        flash('Info', 'info')
        flash('Warning', 'warning')
        flash('Danger', 'danger')
        flash('Success', 'success')
        flash('Multiple\nlines\nin one message', 'info')
        return render_template('base.html')

    @app.before_request
    def init_app_settings():
        """
        Redirect any endpoint to update application settings if any not set.
        """
        if (
            request.endpoint is not None
            and
            (
                request.endpoint in 'static'
                or
                request.endpoint.startswith('auth.')
            )):
            return

        missing_form_class = ApplicationSetting.missing_settings_form()
        if missing_form_class:
            if request.endpoint == 'app_settings.edit_required_settings':
                return
            return redirect(url_for('app_settings.edit_required_settings'))

    def announcements():
        """
        Flash all announcements from database.
        """
        if request.endpoint and request.endpoint.startswith('admin'):
            return

        flashed = flask_session.get('flashed', list())
        now = timezone.now()
        announcements = Announcement.all_active_for(now)
        for announcement in announcements:
            if str(announcement.id) not in flashed:
                flashed.append(str(announcement.id))
                flash(announcement.message, announcement.level.name)

        flask_session['flashed'] = flashed

    return app
