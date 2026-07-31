from datetime import datetime

from wtforms import BooleanField
from wtforms import DateTimeField
from wtforms import FieldList
from wtforms import StringField


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


class ISODateTimeField(StringField):

    def __init__(self, *args, timespec=None, **kwargs):
        self.timespec = timespec
        super().__init__(*args, **kwargs)

    def process_data(self, value):
        if isinstance(value, datetime):
            self.data = value.isoformat(timespec=self.timespec)
        else:
            self.data = value or ""

    def _value(self):
        return self.data or ""
