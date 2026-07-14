import time

import click

from flask import render_template
from flask import current_app

from jumpseat_request import settings
from jumpseat_request.extension import db
from jumpseat_request.extension import smtp
from jumpseat_request.extension import timezone
from jumpseat_request.model import EmailJob
from jumpseat_request.model import EmailJobRecipient
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.secret import six_digit_code

@click.command("jobs")
@click.option('--sleep-time', type=float, help='Sleep time between loops.')
def background_jobs(sleep_time):
    """
    Background service to send emails and escalate jumpseat requests.
    """
    if not sleep_time:
        sleep_time = current_app.config.get('SEND_EMAIL_SLEEP', 0.5)
    current_app.logger.info(f'Starting email sending service {smtp.smtp_args}')
    while True:
        # Send escalation signals.
        JumpseatRequest.escalate_as_needed(timezone.now())
        # Send emails that are ready.
        EmailJob.send_one_pending()
        time.sleep(sleep_time)

@click.command('escalate-requests')
def escalate_requests():
    """
    Create EmailJob objects for requests that need to escalate to configured
    emails.
    """
    for jumpseat_requests in JumpseatRequest.needs_escalation(timezone.now()):
        pass

def init_app(app):
    """
    Add service commands to flask.
    """
    app.cli.add_command(background_jobs)
    app.cli.add_command(escalate_requests)
