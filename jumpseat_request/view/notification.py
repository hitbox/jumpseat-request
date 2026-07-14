import click

from flask import Blueprint

from jumpseat_request.extension import db
from jumpseat_request.model import NotificationRecipient
from jumpseat_request.model import NotificationRule
from jumpseat_request.model import User

notification_bp = Blueprint('notification', __name__)

notification_bp.cli.help = 'Administrate notification rules and their recipients.'

@notification_bp.cli.command('create')
@click.option('--name', required=True, help='Notification rule name.')
@click.option('--blurb', required=True, help='Notification comment.')
@click.option('--signal-name', required=True, help='Internal signal event name.')
@click.option('--created-age', required=False, help='Age of request in seconds, to fire this rule.')
def create_notification_rule(name, blurb, signal_name, created_age):
    """
    Create a named notification rule.
    """
    notification_rule = NotificationRule(
        name = name,
        blurb = blurb,
        signal_name = signal_name,
        created_at_age_seconds = created_age,
    )
    db.session.add(notification_rule)
    db.session.commit()

@notification_bp.cli.command('add-recipient')
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

@notification_bp.cli.command('list-rules')
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
