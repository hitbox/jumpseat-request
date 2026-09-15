from markupsafe import Markup
from markupsafe import escape

def mailto(email_address):
    return Markup(f'<a href="mailto:{email_address}">{email_address}</a>')

def render_attrs(**kwargs):
    """
    Render html element attributes.
    """
    parts = []
    for k, v in kwargs.items():
        if v is True:
            parts.append(k)  # boolean attr
        elif v is False or v is None:
            continue
        else:
            parts.append(f'{k}="{escape(v)}"')
    return Markup(" ".join(parts))

