from datetime import datetime

from wtforms import BooleanField
from wtforms import DateTimeField
from wtforms import FieldList
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import ValidationError


class DynamicFieldList(FieldList):
    """
    Subclass FieldList to detect and render with special template.
    """


def switch_field(**kwargs):
    render_kw = kwargs.setdefault('render_kw', {})
    render_kw.setdefault('role', 'switch')
    return BooleanField(**kwargs)

def delete_submit_field(**kwargs):
    render_kw = kwargs.setdefault('render_kw', {})
    render_kw.setdefault('class', 'contrast')
    return SubmitField(**kwargs)

class TimezoneDateTimeField(DateTimeField):

    def __init__(self, *args, timezone=None, **kwargs):
        self.timezone = timezone
        super().__init__(*args, **kwargs)

    def process_formdata(self, valuelist):
        super().process_formdata(valuelist)

        if self.data is not None and self.timezone:
            self.data = self.data.replace(tzinfo=self.timezone)


class ISODateTimeField(StringField):

    def __init__(self, *args, timespec=None, require_offset=False, **kwargs):
        self.timespec = timespec
        self.require_offset = require_offset
        super().__init__(*args, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                dt = datetime.fromisoformat(valuelist[0])
            except ValueError as e:
                raise ValidationError(f'Invalid ISO 8601 datetime') from e

            if self.require_offset and dt.tzinfo is None:
                raise ValidationError(f'Missing timezone offset')

            self.data = dt
        else:
            self.data = None

    def _value(self):
        if self.data:
            return self.data.isoformat(timespec=self.timespec)
        else:
            return ''
