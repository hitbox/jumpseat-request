from email.message import EmailMessage

import uuid

from flask import current_app
from flask import render_template
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from jumpseat_request import settings
from jumpseat_request.extension import db
from jumpseat_request.extension import smtp
from jumpseat_request.extension import timezone
from jumpseat_request.settings import from_address

from .mixin import ModelMixin

class EmailJobRecipient(db.Model):
    """
    A recipient (to-address) for an email job.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
        info = {
            'is_hidden': True,
        },
    )

    email_job_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('email_job.id'),
    )

    email_address = db.Column(
        db.String,
        nullable = False,
    )


class EmailJob(db.Model, ModelMixin):
    """
    Queued email delivery job.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
        info = {
            'is_hidden': True,
        },
    )

    subject = db.Column(
        db.String,
        nullable = False,
    )

    from_email_address = db.Column(
        db.String,
        nullable = False,
    )

    recipient_objects = db.orm.relationship(
        'EmailJobRecipient',
    )

    recipients = association_proxy(
        'recipient_objects',
        'email_address',
        creator = lambda email_address: EmailJobRecipient(email_address=email_address)
    )

    body_text = db.Column(
        db.String,
        nullable = False,
    )

    body_html = db.Column(
        db.String,
        nullable = True,
    )

    processing_at = db.Column(
        db.DateTime(timezone=True),
        nullable = True,
        comment = 'Datetime mark when background service began trying to send this email.',
    )

    sent_at = db.Column(
        db.DateTime(timezone=True),
        nullable = True,
        comment = 'Email successfully sent datetime.',
    )

    @property
    def sent_at_formatted(self):
        if self.sent_at:
            return self.sent_at.strftime(settings.datetime_format())

    failed_at = db.Column(
        db.DateTime(timezone=True),
        nullable = True,
        comment = 'Last failure datetime to send email.',
    )

    failed_exception = db.Column(
        db.String,
        nullable = True,
    )

    @classmethod
    def pending(cls):
        """
        Return list of pending (ready unsent) emails.
        """
        query = db.select(cls).where(
            cls.processing_at.is_(None),
            cls.sent_at.is_(None),
        )
        return db.session.scalars(query).all()

    def to_python_email_message(self):
        message = EmailMessage()

        message['Subject'] = self.subject
        message['From'] = self.from_email_address
        message['To'] = ', '.join(self.recipients)

        message.set_content(self.body_text)

        if self.body_html:
            message.add_alternative(self.body_html, subtype='html')

        return message

    @classmethod
    def from_proposal_created(cls, jumpseat_request_proposal):
        data = jumpseat_request_proposal.data

        inst = cls()
        inst.subject = 'Jumpseat Request Created'
        inst.from_email_address = from_address()
        inst.recipients = [
            data['employee']['email_address'],
        ]

    @classmethod
    def send_one_pending(cls):
        """
        Send one of any pending email jobs. Return True if any email was sent,
        False otherwise.
        """
        query = (
            db.select(cls)
            .where(
                cls.sent_at.is_(None),
                cls.failed_at.is_(None),
            )
            .with_for_update(skip_locked=True)
            .limit(1)
        )

        email_job = db.session.scalars(query).first()

        if not email_job:
            return False

        current_app.logger.info('Got email job %s', email_job.id)
        email_job.processing_at = timezone.now()

        try:
            message = email_job.to_python_email_message()
            smtp.send_message(message)
            email_job.sent_at = timezone.now()
            return True

        except Exception as e:
            # release job for retry
            email_job.processing_at = None
            current_app.logger.exception(
                "EmailJob failed id: %s", email_job.id
            )
            email_job.failed_at = timezone.now()
            email_job.failed_exception = str(e)

        finally:
            db.session.commit()

    @classmethod
    def create_email_verification(
        cls,
        email_address,
        token,
        recipients,
        body_text_template = 'email_verification.txt',
        body_html_template = 'email_verification.html',
    ):
        context = {
            'email_address': email_address,
            'token': token,
        }
        body_text = render_template(body_text_template, **context)
        body_html = render_template(body_html_template, **context)
        inst = cls(
            subject = 'Verify Email',
            from_email_address = from_address(),
            recipients = recipients,
            body_text = body_text,
            body_html = body_html,
        )
        return inst
