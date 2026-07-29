from wtforms import BooleanField
from wtforms import FieldList

class DynamicFieldList(FieldList):
    """
    Subclass FieldList to detect and render with special template.
    """

def switch_field(**kwargs):
    render_kw = kwargs.setdefault('render_kw', {})
    render_kw.setdefault('role', 'switch')
    return BooleanField(**kwargs)
