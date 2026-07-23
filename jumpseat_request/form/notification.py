from flask_wtf import FlaskForm
from wtforms import FormField
from wtforms import IntegerField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import Optional

from jumpseat_request.model import NotificationRecipient
from jumpseat_request.signal import jumpseat_request_signals

from .mixin import OrderedFieldsMixin
from .field import DynamicFieldList

class NotificationRecipientSubform(FlaskForm):
    """
    Email address to send notification rule.
    """
    class Meta:
        csrf = False

    email_address = StringField(
        render_kw = {
            'title': 'email address or format string',
            'data-name-template': 'recipients-{__index__}-email_address',
        },
    )


class EditNotificationRuleForm(FlaskForm):
    """
    Edit Notification Rule object.
    """

    name = StringField()

    blurb = StringField()

    signal_name = SelectField(
        'Signal',
        choices = list(jumpseat_request_signals),
    )

    created_at_age_seconds = IntegerField(
        'Created Age Seconds',
        validators = [
            Optional(),
        ],
        render_kw = {
            'placeholder': 'Seconds after request created to fire this notification. Leave blank for non-applicable signals.',
        },
    )

    recipients = DynamicFieldList(
        FormField(
            NotificationRecipientSubform,
        ),
        render_kw = {
            'data-tooltip': 'Hello!',
        }
    )

    update = SubmitField()

    def populate_obj(self, notification_rule):
        for field in self:
            if field.name == 'recipients':
                continue
            field.populate_obj(notification_rule, field.name)

        notification_rule.recipients = [
            NotificationRecipient.get_or_create_for_email(
                email_address = subform.email_address.data,
                notification_rule = notification_rule,
            )
            for subform in self.recipients
        ]
