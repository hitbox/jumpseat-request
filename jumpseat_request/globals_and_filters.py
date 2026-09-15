import re

from datetime import datetime
from datetime import timedelta

from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from wtforms import BooleanField
from wtforms import FieldList
from wtforms import FormField

from .form.field import DynamicFieldList
from .settings import date_format
from .settings import datetime_format
from htmlkit import render_attrs

def format_datetime_as_configured(dt):
    if not dt:
        return ''

    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)

    return dt.strftime(datetime_format())

def format_date_as_configured(dt):
    if not dt:
        return ''

    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)

    return dt.strftime(date_format())

def render_formfield(field):
    return Markup(render_template('formfield.html', field=field))

def render_fieldlist(field):
    """
    Render wtforms.FieldList with special template.
    """
    prototype_form = field.unbound_field.args[0]()
    context = {
        'field': field,
        'prototype_form': prototype_form,
    }
    return Markup(render_template('fieldlist.html', **context))

def render_field(field):
    if isinstance(field, DynamicFieldList):
        return render_fieldlist(field)

    if isinstance(field, FormField):
        return render_formfield(field)

    html = ['<div class="group">']

    if isinstance(field, BooleanField):
        # Reverse order elements for booleans
        html.append(field())
        html.append(str(field.label))
    else:
        html.append(str(field.label))
        html.append(field())

    if field.errors:
        html.append('<div class="field-errors">')
        for error_message in field.errors:
            html.append(f'<div class="field-error danger">{ error_message }</div>')
        html.append('</div>')

    html.append('</div>')
    return Markup(''.join(html))

def nav_links():
    links = []

    if current_user.is_authenticated:
        # Jumpseat request page
        links.append({
            'url' : url_for('jumpseat_request.landing_page'),
            'text': 'Request',
            'current_for_pattern': 'jumpseat_request.landing_page',
            'data-tooltip': 'Submit a jumpseat request.',
            'data-placement': 'bottom',
        })
        if current_user.is_decider:
            links.append({
                'url' : url_for('jumpseat_request.list_jumpseat_requests'),
                'text' : 'Decide',
                'current_for_pattern' : 'jumpseat_request.list_jumpseat_requests_list',
                'data-tooltip': 'Approve or disapprove jumpseat requests.',
                'data-placement': 'bottom',
            })
            links.append({
                'url' : url_for('jumpseat_request.approved_requests'),
                'text' : 'Export',
                'data-tooltip': 'Export requested jumpseats for a date range.',
                'data-placement': 'bottom',
                'current_for_pattern' : 'jumpseat_request.approved_requests',
            })
        # Authenticated user profile page
        links.append({
            'url' : url_for('user.profile'),
            'text': 'Profile',
            'current_for_pattern': 'user.profile', # FIXME: make any sense for logout?
            'data-tooltip': 'Login/logout and edit account',
            'data-placement': 'bottom',
        })
        if current_user.is_admin:
            # Admin page
            links.append({
                'url' : url_for('admin.root'),
                'text': 'Admin',
                'current_prefix': 'admin.',
                'data-tooltip': 'Administration page for jumpseat request application.',
                'data-placement': 'bottom',
            })
    else:
        links.append({
            'url': url_for('auth.login'),
            'text': 'Login',
            'current_for_pattern': 'auth.login',
            'data-tooltip': 'Login as existing user',
            'data-placement': 'bottom',
        })
        links.append({
            'url': url_for('user.create_account'),
            'text': 'Create account',
            'current_for_pattern': 'user.create_account',
        })

    return links

def render_link_with_current(url, text, current_for_pattern=None, **attributes):
    """
    Template link renderer.
    """
    if current_for_pattern is not None:
        if re.match(request.endpoint, current_for_pattern):
            attributes.setdefault('aria-current', 'page')

    return Markup(f'<a {render_attrs(**attributes)} href="{url}">{ text }</a>')

def ordinal(n):
    suffixes = {
        1: 'st',
        2: 'nd',
        3: 'rd',
    }
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = suffixes.get(n % 10, 'th')
    return f'{n}{suffix}'

def init_app(app):
    """
    Add jinja template filters and globals.
    """
    app.jinja_env.filters['format_datetime_as_configured'] = format_datetime_as_configured
    app.jinja_env.filters['format_date_as_configured'] = format_date_as_configured
    app.jinja_env.globals['render_field'] = render_field
    app.jinja_env.globals['render_link_with_current'] = render_link_with_current
    app.jinja_env.globals['nav_links'] = nav_links
    app.jinja_env.globals['ordinal'] = ordinal
    app.jinja_env.globals['timedelta'] = timedelta
