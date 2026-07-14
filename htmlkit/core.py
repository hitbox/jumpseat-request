from markupsafe import Markup

def mailto(email_address):
    return Markup(f'<a href="mailto:{email_address}">{email_address}</a>')
