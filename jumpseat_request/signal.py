from blinker import Namespace

from .subscriber import EmailSubscriber

jumpseat_request_signals = Namespace()

jumpseat_request_created = jumpseat_request_signals.signal('jumpseat-request-created')

jumpseat_request_escalate = jumpseat_request_signals.signal('jumpseat-request-escalate')

jumpseat_request_decided = jumpseat_request_signals.signal('jumpseat-request-decided')

created_subscriber = EmailSubscriber(
    subject = 'Jump Seat Request Created',
    text_body_template = 'request_created.txt',
    html_body_template = 'request_created.html',
)

jumpseat_request_created.connect(created_subscriber)

decided_subscriber = EmailSubscriber(
    subject = 'Jump Seat Request {jumpseat_request_status}',
    text_body_template = 'request_decided.txt',
    html_body_template = 'request_decided.html',
)

jumpseat_request_decided.connect(decided_subscriber)

escalated_subscriber = EmailSubscriber(
    subject = 'Jump Seat Request Elevated',
    text_body_template = 'request_decided.txt',
    html_body_template = 'request_decided.html',
)

jumpseat_request_escalate.connect(escalated_subscriber)
