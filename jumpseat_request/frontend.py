"""
Frontend related utilities.
"""
from datetime import datetime
from operator import attrgetter

from flask import url_for
from flask import render_template
from flask import current_app
from markupsafe import Markup

from htmlkit.core import mailto
from htmlkit.lists import definition_list
from htmlkit.lists import unordered_list
from htmlkit.table import Column
from htmlkit.table import Table

type_formatters = {
    datetime: lambda value: value.strftime(''),
    None: lambda value: '',
}

class ValueFormatter:

    def __init__(self, type_formatters):
        if not isinstance(type_formatters, dict):
            raise ValueError(f'Expected dict got {type(type_formatters)}')
        self.type_formatters = type_formatters

    def __call__(self, parent, value):
        for type_, formatter in self.type_formatters.items():
            if type_ is not None and isinstance(value, type_):
                return formatter(parent, value)


def airline_label_getter(airline):
    """
    Configurable Airline object label getter.
    """
    key = 'JUMPSEAT_REQUEST_SHOW_AIRLINE_CODE'
    if key not in current_app.config:
        raise KeyError(f'{key} must be in config')
    attr = current_app.config.get(key, 'icao_code')
    return attrgetter(attr)

def yesno(value):
    """
    Return boolean as Yes/No.
    """
    # TODO: delete isinstance check
    if not isinstance(value, bool):
        raise ValueError(f'Invalid type {type(value)}')
    if value is True:
        return Markup(f'<span class="bool bool-yes">Yes</span>')
    elif value is False:
        return Markup('<span class="bool bool-no">No</span>')

def configured_datetime_formatter(value):
    key = 'JUMPSEAT_REQUEST_DATETIME_FORMAT'
    dtformat = current_app.config.get(key)
    if dtformat:
        return value.strftime(dtformat)
    else:
        return str(value)

def email_verification_objects_links_list(email_verification_objects):
    """
    Render html links to confirm email verification.
    """
    html = []
    for ev in email_verification_objects:
        link = (
            f'<div>'
            f'<a href="{url_for('admin.email_verification_edit', id=ev.id)}">'
            f'<span>Click to confirm email</span></a>'
            f'</div>'
            f'<div>Expires:</div>'
            f'<span>{many_formatter(ev.expire_at)}</span>'
        )
        html.append(link)
    return Markup(''.join(html))

many_formatter = ValueFormatter({
    datetime: lambda parent, value: configured_datetime_formatter(value),
    type(None): lambda parent, value: '(None)',
    type(True): lambda parent, value: yesno(value),
    str: lambda parent, value: str(value)
})
