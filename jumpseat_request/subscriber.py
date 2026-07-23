from flask import render_template

from . import settings
from .extension import db
from .extension import email_verify

class AccountEmailSubscriber:
    """
    Subscribe to account events.
    """

    def __init__(self, text_body_template, html_body_template, subject):
        self.subject = subject
        self.text_body_template = text_body_template
        self.html_body_template = html_body_template

    def __call__(self, sender, user):
        pass


class JumpseatRequestEmailSubscriber:
    """
    Send emails for jumpseat request signals like created and decided.
    """

    def __init__(self, text_body_template, html_body_template, subject, verb=None):
        self.subject = subject
        self.text_body_template = text_body_template
        self.html_body_template = html_body_template
        self.verb = verb

    def __call__(self, sender, jumpseat_request, signal, comment=None):
        """
        Create email job from configured templates for jump seat requests.
        """
        from .model import EmailJob
        from .model import JumpseatRequestNotificationRuleAssoc
        from .model import NotificationRule
        from .model import User

        for notification_rule in NotificationRule.get_by_signal(signal):
            submitter_email = jumpseat_request.employee_email
            context = {
                'comment': comment,
                'jumpseat_request': jumpseat_request,
                'jumpseat_request_status': jumpseat_request.status(),
                'sender': sender,
                'submitter_email': submitter_email,
                'verb': self.verb,
            }
            # Flatten recipient objects to email addresses passing context to
            # allow some to be the things like the subitter's email.
            recipient_emails = [
                recipient.email_address.format(**context)
                for recipient in notification_rule.recipients
            ]

            # User objects for email addresses where available.
            query = (
                db.select(User)
                .where(
                    User.email_address.in_(recipient_emails)
                )
            )
            recipient_users = db.session.scalars(query).all()

            # Flag that an admin is in the recipients.
            users_is_admin = (user.is_admin for user in recipient_users)
            admin_in_recipients = any(users_is_admin)
            context['admin_in_recipients'] = admin_in_recipients

            # Add flag for template if any recipients are decider accounts.
            users_is_decider = (user.is_decider for user in recipient_users)
            context['has_decider_recipient'] = any(users_is_decider)

            # Recipients email addresses list
            recipients = [
                email_string.format(**context)
                for email_string in notification_rule.recipient_emails
            ]

            body_text = render_template(self.text_body_template, **context)
            body_html = render_template(self.html_body_template, **context)

            email_job = EmailJob(
                subject = self.subject.format(**context),
                from_email_address = settings.from_address(),
                recipients = recipients,
                body_text = body_text,
                body_html = body_html,
            )
            db.session.add(email_job)
