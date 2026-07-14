import uuid
 
from flask import current_app
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup
from sqlalchemy.ext.hybrid import hybrid_property

from jumpseat_request import settings
from jumpseat_request.extension import db
from jumpseat_request.extension import timezone
from jumpseat_request.signal import jumpseat_request_decided
from jumpseat_request.signal import jumpseat_request_escalate
from jumpseat_request.signal import jumpseat_request_escalate

from .mixin import ModelMixin
from .user import User

class JumpseatRequest(db.Model, ModelMixin):
    """
    User or guest submitted request for jumpseat on a flight.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    flight_date = db.Column(
        db.Date,
        nullable = False,
    )

    @property
    def flight_date_formatted(self):
        return self.flight_date.strftime(settings.date_format())

    flight_number = db.Column(
        db.String,
        nullable = False,
    )

    employee_airline_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('airline.id'),
        nullable = False,
    )

    employee_airline = db.orm.relationship(
        'Airline',
    )

    @property
    def employee_airline_as_configured(self):
        if self.employee_airline:
            attr = settings.airline_label_attribute()
            return getattr(self.employee_airline, attr)

    employee_number = db.Column(
        db.String,
        nullable = False,
    )

    employee_name = db.Column(
        db.String,
        nullable = True,
    )

    employee_email = db.Column(
        db.String,
        nullable = False,
    )

    employee_phone = db.Column(
        db.String,
        nullable = True,
    )

    request_by_user_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('user.id'),
        nullable = False,
        comment = 'FK id of user who created this jumpseat request.',
    )

    request_by = db.orm.relationship(
        'User',
        foreign_keys = [request_by_user_id],
        back_populates = 'jumpseat_requests',
    )

    approved_at = db.Column(
        db.DateTime(timezone=True),
        nullable = True,
    )

    denied_at = db.Column(
        db.DateTime(timezone=True),
        nullable = True,
    )

    escalated_at = db.Column(
        db.DateTime(timezone=True),
        nullable = True,
    )

    decision_by_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('user.id'),
        comment = 'FK id of user who decided this jumpseat request.',
    )

    decision_by = db.orm.relationship(
        'User',
        foreign_keys = [decision_by_id],
    )

    reason = db.Column(
        db.String,
        nullable = True,
    )

    notifications = db.orm.relationship(
        'JumpseatRequestNotificationRuleAssoc',
        back_populates = 'jumpseat_request',
    )

    @hybrid_property
    def is_decided(self):
        return (~self.approved_at and ~self.denied_at)

    @is_decided.expression
    def is_decided(cls):
        return db.not_(db.and_(cls.approved_at.is_(None), cls.denied_at.is_(None)))

    @classmethod
    def escalate_as_needed(cls, now):
        """
        """
        for jumpseat_request, notification_rule in cls.needs_escalation(now):
            current_app.logger.info(f'escalate signal for {jumpseat_request.id=}')
            jumpseat_request.escalated_at = now
            jumpseat_request_escalate.send(
                cls.escalate_as_needed,
                signal = jumpseat_request_escalate,
                jumpseat_request = jumpseat_request,
                comment =
                    'Request escalated after'
                    f' {notification_rule.created_at_age_seconds} seconds',
            )
            db.session.commit()

    @classmethod
    def needs_escalation(cls, now):
        """
        Return a list of (JumpseatRequest, NotificationRule) pairs for
        notification rules that meet the condition for escalation.
        """
        # Compare all notification rules against pending requests
        from .notification import NotificationRule

        query = (
            db.select(cls, NotificationRule)
            .where(
                NotificationRule.signal_name == jumpseat_request_escalate.name,
                ~cls.is_decided,
                cls.created_at_age_seconds > NotificationRule.created_at_age_seconds,
                cls.escalated_at.is_(None),
            )
        )

        return db.session.execute(query).all()

    def short_html(self):
        """
        Short html blurb of jumpseat request info.
        """
        cancel_endpoint = 'jumpseat_request.cancel_jumpseat_request'
        cancel_url = url_for(cancel_endpoint, request_id=self.id)
        html = [
            f'<span class="data employeer">{ self.data['employee']['airline']['icao_code'] }</span>',
            f' Jumpseat on ',
            f'<span class="data date">{ self.data['flight_date'] }</span>',
            f' for flight ',
            f'<span class="data flight-number">{ self.data['flight_number'] }</span>',
        ]
        return Markup(''.join(html))

    def html_card(self):
        context = {
            'jumpseat_request': self,
        }
        return Markup(render_template('jumpseat_request_card.html', **context))

    def status(self):
        if self.approved_at is not None:
            return 'approved'
        elif self.denied_at is not None:
            return 'denied'
        else:
            return 'pending'

    def status_html(self):
        if self.approved_at is not None:
            return Markup(f'<span class="request-status approved">Approved</span>')
        elif self.denied_at is not None:
            return Markup(f'<span class="request-status denied">Denied</span>')
        else:
            return Markup(f'<span class="request-status pending">Pending</span>')

    def is_undecided(self):
        return self.approved_at is None and self.denied_at is None

    def approve(self):
        """
        Update jumpseat request as approved.
        """
        self.approved_at = timezone.now()
        self.denied_at = None
        jumpseat_request_decided.send(
            self.approve,
            signal = jumpseat_request_decided,
            jumpseat_request=self,
            comment = 'Request approved.',
        )

    def deny(self):
        """
        Update jumpseat request as denied.
        """
        self.approved_at = None
        self.denied_at = timezone.now()
        jumpseat_request_decided.send(
            self.approve,
            signal = jumpseat_request_decided,
            jumpseat_request = self,
            comment = 'Request denied.',
        )

    @classmethod
    def pagination_getter(cls):
        query = (
            db.select(cls)
            .order_by(cls.created_at.desc())
        )
        return db.paginate(query)
