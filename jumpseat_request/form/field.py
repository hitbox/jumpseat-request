from wtforms import BooleanField
from wtforms import FieldList
from wtforms import DateTimeField


class DynamicFieldList(FieldList):
    """
    Subclass FieldList to detect and render with special template.
    """

def switch_field(**kwargs):
    render_kw = kwargs.setdefault('render_kw', {})
    render_kw.setdefault('role', 'switch')
    return BooleanField(**kwargs)

class TimezoneDateTimeField(DateTimeField):

    def __init__(self, *args, timezone=None, **kwargs):
        self.timezone = timezone
        super().__init__(*args, **kwargs)

    def process_formdata(self, valuelist):
        super().process_formdata(valuelist)

        if self.data is not None and self.timezone:
            self.data = self.data.replace(tzinfo=self.timezone)
