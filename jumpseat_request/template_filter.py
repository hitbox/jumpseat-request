from datetime import datetime

from flask import render_template
from markupsafe import Markup
from wtforms import BooleanField
from wtforms import FieldList
from wtforms import FormField

from .form.field import DynamicFieldList
from .settings import date_format
from .settings import datetime_format

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
        html.append(field())
        html.append(str(field.label))
    else:
        html.append(str(field.label))
        html.append(field())
    if field.errors:
        html.append('<div>')
        for error_message in field.errors:
            html.append(f'<div class="danger">{ error_message }</div>')
        html.append('</div>')
    html.append('</div>')
    return Markup(''.join(html))

def init_app(app):
    """
    Add jinja template filters and globals.
    """
    app.jinja_env.filters['format_datetime_as_configured'] = format_datetime_as_configured
    app.jinja_env.filters['format_date_as_configured'] = format_date_as_configured
    app.jinja_env.globals['render_field'] = render_field

