import time

import click

from flask import current_app

from jumpseat_request import settings
from jumpseat_request.extension import smtp
from jumpseat_request.model import EmailJob
from jumpseat_request.model import JumpseatRequest

@click.command("jobs")
@click.option('--sleep-time', type=float, help='Sleep time between loops.')
def background_jobs(sleep_time):
    """
    Background service to send emails and escalate jumpseat requests.
    """
    if sleep_time is None:
        sleep_time = settings.job_sleep_time()
    current_app.logger.info(f'Starting email sending service {smtp.smtp_args}')
    while True:
        # Send escalation signals.
        JumpseatRequest.escalate_as_needed()
        # Send emails that are ready.
        EmailJob.send_one_pending()
        time.sleep(sleep_time)

def init_app(app):
    """
    Add service/task commands to flask.
    """
    app.cli.add_command(background_jobs)
