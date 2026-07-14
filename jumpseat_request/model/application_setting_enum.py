from enum import Enum

from wtforms import IntegerField
from wtforms import StringField
from wtforms.validators import DataRequired

class ApplicationSettingEnum(Enum):
    FROM_ADDRESS = 'from_address'

    TOKEN_MAX_AGE = 'token_max_age'

    APPROVE_COMMENT = 'approve_comment'

    DENY_COMMENT = 'deny_comment'


ApplicationSettingEnum.FROM_ADDRESS.form_field = StringField(
    'From Address',
    validators = [
        DataRequired()
    ],
    render_kw = {
        'title':
            'The email address that appear as the'
            ' from-address for emails.',
    }
)

ApplicationSettingEnum.APPROVE_COMMENT.form_field = StringField(
    'Comment for approval',
    default = 'Request approved',
    validators = [
        DataRequired()
    ],
    render_kw = {
        'title':
            'Short descriptive message for notification of request approval.',
    },
)

ApplicationSettingEnum.DENY_COMMENT.form_field = StringField(
    'Comment for denial',
    default = 'Request denied',
    validators = [
        DataRequired()
    ],
    render_kw = {
        'title':
            'Short descriptive message for notification of request denial.',
    },
)


ApplicationSettingEnum.TOKEN_MAX_AGE.form_field = IntegerField(
    'Token age seconds',
    default = 60,
    validators = [
        DataRequired()
    ],
    render_kw = {
        'title':
            'Maximum age in seconds for email verification token and other time-sensitive links sent to email like registering a guest account.',
    },
)
