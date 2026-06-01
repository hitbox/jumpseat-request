from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for

from . import extension
from .middleware import PrefixMiddleware
from . import view

def create_app():
    app = Flask(__name__)

    app.config.from_envvar('JUMPSEAT_REQUEST_CONFIG')

    extension.init_app(app)
    PrefixMiddleware.init_app(app)
    view.init_app(app)

    @app.route('/')
    def root():
        return redirect(url_for('login.user_account'))

    @app.route('/messages')
    def messsages():
        flash('Info', 'info')
        flash('Warning', 'warning')
        flash('Danger', 'danger')
        return render_template('base.html')

    return app
