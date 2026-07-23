from blinker import Namespace
from flask import current_app

from .extension import db
from .extension import email_verify
from .model import EmailJob
from .subscriber import JumpseatRequestEmailSubscriber

jumpseat_request_signals = Namespace()

jumpseat_request_created = jumpseat_request_signals.signal('jumpseat-request-created')

jumpseat_request_escalate = jumpseat_request_signals.signal('jumpseat-request-escalate')

jumpseat_request_decided = jumpseat_request_signals.signal('jumpseat-request-decided')

account_creation_requested = jumpseat_request_signals.signal('create-account-request')

email_verified = jumpseat_request_signals.signal('email-verified')

account_created_by_user = jumpseat_request_signals.signal('account-created-by-user')

text_body_template = 'request_event.txt'
html_body_template = 'request_event.html'

created_subscriber = JumpseatRequestEmailSubscriber(
    subject = 'Jump Seat Request Created',
    text_body_template = text_body_template,
    html_body_template = html_body_template,
    verb = 'created',
)

jumpseat_request_created.connect(created_subscriber)

decided_subscriber = JumpseatRequestEmailSubscriber(
    subject = 'Jump Seat Request {jumpseat_request_status}',
    text_body_template = text_body_template,
    html_body_template = html_body_template,
    verb = 'decided',
)

jumpseat_request_decided.connect(decided_subscriber)

escalated_subscriber = JumpseatRequestEmailSubscriber(
    subject = 'Jump Seat Request Elevated',
    text_body_template = text_body_template,
    html_body_template = html_body_template,
    verb = 'elevated',
)

jumpseat_request_escalate.connect(escalated_subscriber)

@account_creation_requested.connect
def create_account_request(sender, email_address, **kwargs):
    """
    User has submitted an email address for account creation. Send a special
    link to their inbox to verify email.
    """
    # TODO
    payload = {
        'email_address': email_address,
    }
    token = email_verify.create_token(payload=payload)
    email_job = EmailJob.create_email_verification(
        email_address = email_address,
        token = token,
        recipients = [email_address],
    )
    db.session.add(email_job)
    db.session.commit()
    current_app.logger.info('EmailJob created, email_job.id=%s', email_job.id)
