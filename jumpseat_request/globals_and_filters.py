from datetime import datetime
from datetime import timedelta

from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from markupsafe import escape
from wtforms import BooleanField
from wtforms import FieldList
from wtforms import FormField

from .form.field import DynamicFieldList
from .settings import date_format
from .settings import datetime_format

def render_attrs(**kwargs):
    parts = []
    for k, v in kwargs.items():
        if v is True:
            parts.append(k)  # boolean attr
        elif v is False or v is None:
            continue
        else:
            parts.append(f'{k}="{escape(v)}"')
    return Markup(" ".join(parts))

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
        # Reverse order elements for bools
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
        if current_user.is_decider:
            links.append({
                'url' : url_for('jumpseat_request.list_jumpseat_requests'),
                'text' : 'Decide',
                'current_for' : set([
                    'jumpseat_request.list_jumpseat_requests_list'
                ]),
            })
        # Jumpseat request page
        links.append({
            'url' : url_for('jumpseat_request.landing_page'),
            'text': 'Request',
            'current_for': set([
                'jumpseat_request.landing_page'
            ]),
        })
        # Authenticated user profile page
        links.append({
            'url' : url_for('user.profile'),
            'text': 'Profile',
            'current_for': set([
                'user.profile' # FIXME: make any sense for logout?
            ]),
        })
        if current_user.is_admin:
            # Admin page
            links.append({
                'url' : url_for('admin.root'),
                'text': 'Admin',
                'current_prefix': 'admin.',
            })
    else:
        links.append({
            'url': url_for('user.create_account'),
            'text': 'Create account',
            'current_for': set([
                'user.create_account',
            ]),
        })

    return links

def render_link_with_current(url, text, current_for=None, current_prefix=None):
    if current_for is None:
        current_for = set()
    attributes = {}
    if request.endpoint in current_for:
        attributes['aria-current'] = 'page'

    elif current_prefix is not None and request.endpoint.startswith(current_prefix):
        attributes['aria-current'] = 'page'

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
