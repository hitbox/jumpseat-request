import csv

import click

from flask import Blueprint

from jumpseat_request.extension import db
from jumpseat_request.model import Leg
from jumpseat_request.model import NotificationRecipient
from jumpseat_request.model import NotificationRule
from jumpseat_request.model import User
from jumpseat_request.signal import jumpseat_request_signals

lufthansa_bp = Blueprint('lufthansa', __name__)

lufthansa_bp.cli.help = 'Administrate external Lufthansa database related data.'

@lufthansa_bp.cli.command('create-db')
def create_db():
    db.engines['lsyrept'].echo = True
    db.create_all('lsyrept')
    click.echo('Created schema for lsyrept')

@lufthansa_bp.cli.command('load')
@click.argument(
    'sourcepath',
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
    ),
)
def load(sourcepath):
    """
    Load lufthansa Leg table data from CSV taking only the fields that are
    mapped.
    """
    with open(sourcepath, 'r', newline='') as sourcefile:
        mapper = db.inspect(Leg)
        take_keys = set([c.key for c in mapper.columns])
        reader = csv.DictReader(sourcefile)
        for row_data in reader:
            data = {
                key.lower(): value
                for key, value in row_data.items()
                if key.lower() in take_keys
            }
            instance = Leg(**data)
            db.session.add(instance)
        db.session.commit()

@lufthansa_bp.cli.command('create')
@click.option('--name', required=True, help='Notification rule name.')
@click.option('--blurb', required=True, help='Notification comment.')
@click.option('--signal-name', required=True, help='Internal signal event name.')
@click.option('--created-age', required=False, help='Age of request in seconds, to fire this rule.')
def create_notification_rule(name, blurb, signal_name, created_age):
    """
    Create a named notification rule.
    """
    # Validate signal_name
    if signal_name not in jumpseat_request_signals:
        click.echo(f'{signal_name} not in {jumpseat_request_signals=}')
        raise click.Abort()

    notification_rule = NotificationRule(
        name = name,
        blurb = blurb,
        signal_name = signal_name,
        created_at_age_seconds = created_age,
    )
    db.session.add(notification_rule)
    db.session.commit()

@lufthansa_bp.cli.command('add-recipient')
@click.argument('name')
@click.option('--email-address', required=True, help='Email address to add to notification rule.')
@click.option('--force', is_flag=True)
def add_recipient(name, email_address, force):
    """
    Add email recipient to a notification rule.
    """
    email_obj = db.session.scalars(
        db.select(User)
        .where(User.email_address == email_address)
    ).one_or_none()

    if not force and email_obj is None:
        if not click.confirm(f'Email {email_address!r} not found in users. Continue?'):
            return

    query = db.select(NotificationRule).where(
        NotificationRule.name == name
    )
    notification_rule = db.session.scalars(query).one_or_none()
    if notification_rule is None:
        click.echo(f'NotificationRule object for {name=} not found.')
        raise click.Abort()

    notification_rule.recipients.append(NotificationRecipient(email_address=email_address))
    db.session.commit()

@lufthansa_bp.cli.command('list-rules')
@click.option('--with-emails', is_flag=True)
def add_recipient(with_emails):
    """
    List all notification rules by name.
    """
    query = db.select(NotificationRule)
    for notification_rule in db.session.scalars(query):
        click.echo(notification_rule.name)
        if with_emails:
            for email in notification_rule.recipient_emails:
                click.echo(f'\t{email}')
