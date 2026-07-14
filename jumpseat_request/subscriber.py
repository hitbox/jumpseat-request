from flask import render_template

from . import settings
from .extension import db
from .extension import email_verify

class EmailSubscriber:
    """
    Send emails for jumpseat request signals like created and decided.
    """

    def __init__(self, text_body_template, html_body_template, subject):
        self.subject = subject
        self.text_body_template = text_body_template
        self.html_body_template = html_body_template

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
                'jumpseat_request': jumpseat_request,
                'jumpseat_request_status': jumpseat_request.status(),
                'sender': sender,
                'comment': comment,
                'submitter_email': submitter_email,
            }

            # Flatten recipient objects to email addresses
            recipient_emails = [recipient.email_address.format(**context) for recipient in notification_rule.recipients]

            # Flag that an admin is in the recipients.
            admin_in_recipients = any(User.by_email(email).is_admin == True for email in recipient_emails if User.by_email(email))
            context['admin_in_recipients'] = admin_in_recipients

            if jumpseat_request.request_by.is_guest:
                submitter_in_recipients = any(email == jumpseat_request.employee_email for email in recipient_emails)
                if submitter_in_recipients:
                    # Give the submitter_email the guest token link to register
                    guest_verfiy_email_token = email_verify.create_token(
                        email = submitter_email,
                        user_id = str(jumpseat_request.request_by.id),
                        jumpseat_request_id = str(jumpseat_request.id),
                    )
                    context['guest_verfiy_email_token'] = guest_verfiy_email_token

            # Add flag for template if any recipients are decider accounts.
            for recipient in notification_rule.recipients:
                user = User.by_email(recipient.email_address)
                if user and user.is_decider:
                    context['has_decider_recipient'] = True
                    break

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
