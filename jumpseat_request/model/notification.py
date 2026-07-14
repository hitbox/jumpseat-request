import uuid

from argon2 import PasswordHasher
from argon2 import exceptions as password_exceptions
from flask_login import UserMixin
from sqlalchemy.ext.associationproxy import association_proxy

from jumpseat_request.extension import db
from jumpseat_request.signal import jumpseat_request_signals

from .mixin import ModelMixin

password_hasher = PasswordHasher()

class NotificationRule(db.Model, ModelMixin):
    """
    A notification rule to group email address recipients to a notification
    event. 
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    name = db.Column(
        db.String,
        nullable = False,
        unique = True,
        comment = 'Unique short name for notification rule.',
    )

    blurb = db.Column(
        db.String,
        comment = 'Short comment for notification rule.',
    )

    # Not unique to allow multiple notifications for the same signal.
    signal_name = db.Column(
        db.String,
        nullable = False,
        comment = 'Blinker signal name.',
    )

    @db.validates('signal_name')
    def validate_signal_name(self, key, value):
        if value not in jumpseat_request_signals:
            raise ValueError(f'{value} not in {jumpseat_request_signals.keys()=}')
        return value

    @classmethod
    def get_by_signal(cls, signal):
        query = db.select(cls).where(cls.signal_name == signal.name)
        instances = db.session.scalars(query).all()
        return instances

    created_at_age_seconds = db.Column(
        db.Float,
        nullable = True, # null for no condition on age of request.
        comment = 'Only send notification if jumpseat request is at least this old in seconds.',
    )

    recipients = db.orm.relationship(
        'NotificationRecipient',
        back_populates = 'notification_rule',
        cascade = 'all, delete-orphan',
    )

    recipient_emails = association_proxy(
        'recipients',
        'email_address',
    )


class NotificationRecipient(db.Model, ModelMixin):

    __table_args__ = (
        db.UniqueConstraint(
            # unique email per notification
            'notification_rule_id',
            'email_address',
        ),
    )

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    notification_rule_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('notification_rule.id'),
        nullable = False,
    )

    notification_rule = db.orm.relationship(
        'NotificationRule',
        back_populates = 'recipients',
    )

    email_address = db.Column(
        db.String,
        nullable = False,
    )

    def __init__(self, email_address, **kwargs):
        super().__init__(**kwargs)
        self.email_address = email_address

    @classmethod
    def get_or_create_for_email(cls, email_address, notification_rule):
        select_email = (
            db.select(cls)
            .where(
                # Unique emails per NotificationRule (our parent).
                cls.email_address == email_address,
                cls.notification_rule == notification_rule,
            )
        )
        instance = db.session.scalars(select_email).one_or_none()
        if instance is None:
            instance = cls(email_address=email_address)
        return instance


class JumpseatRequestNotificationRuleAssoc(db.Model, ModelMixin):
    """
    A record of the notifications that were created.
    """

    __name_for_template__ = 'Notification for Jumpseat Request'

    jumpseat_request_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('jumpseat_request.id'),
        primary_key = True,
    )

    jumpseat_request = db.orm.relationship(
        'JumpseatRequest',
    )

    notification_rule_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('notification_rule.id'),
        primary_key = True,
    )

    notification_rule = db.orm.relationship(
        'NotificationRule',
    )

    message = db.Column(
        db.String,
        nullable = False,
        comment = 'Message describing the notification.',
    )
