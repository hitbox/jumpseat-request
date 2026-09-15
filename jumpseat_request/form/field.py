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

def fixup_isoformat_string(string):
    """
    Try to pad iso datetime string with zeros.
    """
    if 'T' in string:
        date_string, time_string = string.split('T', 2)

        date_parts = date_string.split('-')
        date_parts = [part.zfill(2) for part in date_parts]

        date_string = '-'.join(date_parts)

        time_string, offset_string = time_string.split('-')

        time_parts = time_string.split(':')
        time_parts = [part.zfill(2) for part in time_parts]

        time_string = ':'.join(time_parts)

        offset_parts = offset_string.split(':')
        offset_parts = [part.zfill(2) for part in offset_parts]

        offset_string = ':'.join(offset_parts)

        string = f'{date_string}T{time_string}-{offset_string}'

    return string

class TimezoneDateTimeField(DateTimeField):

    def __init__(self, *args, timezone=None, **kwargs):
        self.timezone = timezone
        super().__init__(*args, **kwargs)

    def process_formdata(self, valuelist):
        super().process_formdata(valuelist)

        if self.data is not None and self.timezone:
            self.data = self.data.replace(tzinfo=self.timezone)


class ISODateTimeField(StringField):
    """
    ISO 8601 format datetime form field.
    """

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
