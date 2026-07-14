import uuid

from enum import Enum

import humanize

from argon2 import exceptions as password_exceptions
from flask import current_app
from flask import flash
from flask_login import UserMixin
from markupsafe import Markup

from jumpseat_request.extension import db

from .mixin import ModelMixin

class AnnouncementLevelType(Enum):
    # Subset of available css styled flash categories.

    INFO = 'info'
    WARNING = 'warning'
    DANGER = 'danger'


class AnnouncementLevel(db.Model, ModelMixin):
    """
    The level of the announcement indicating it's severity and intent.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
        info = {
            'is_hidden': True,
        },
    )

    name = db.Column(
        db.String,
        unique = True,
        nullable = False,
        comment = 'Short name for announcement.',
    )

    announcements = db.orm.relationship(
        'Announcement',
        back_populates = 'level',
    )


class Announcement(db.Model, ModelMixin):
    """
    An announcement to all or some users.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    is_active = db.Column(
        db.Boolean,
        nullable = False,
        default = True,
        comment =
            'Announcement is active and will be shown'
            ' during it\'s datetime range.',
    )

    starts_at = db.Column(
        db.DateTime(timezone=True),
        comment = 'The datetime the announcement will begin showing.',
    )

    @property
    def human_datetime_range(self):
        text = []
        if self.starts_at is None:
            text.append('forever ago')
        else:
            text.append(humanize.naturaltime(self.starts_at))

        text.append('to')

        if self.ends_at is None:
            text.append('forever')
        else:
            text.append(humanize.naturaltime(self.ends_at))

        return ' '.join(text)

    @property
    def human_datetime_range_html(self):
        """
        Same as human_datetime_range with hover title for specifics.
        """
        html = [f'<div title="From: { self.starts_at } To: { self.ends_at }">']
        html.append(self.human_datetime_range)
        html.append('</div>')
        return Markup(''.join(html))

    ends_at = db.Column(
        db.DateTime(timezone=True),
        comment = 'The datetime the announcement will stop showing.',
    )

    level_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('announcement_level.id'),
        nullable = False,
        comment = 'FK to the level/severity of an announcement',
    )

    level = db.orm.relationship(
        'AnnouncementLevel',
        back_populates = 'announcements',
    )

    title = db.Column(
        db.String,
        nullable = False,
        comment = 'Announcement message title',
    )

    message = db.Column(
        db.String,
        nullable = False,
        comment = 'Announcement message text',
    )

    @classmethod
    def all_active_for(cls, now):
        query = (
            db.select(cls)
            .where(
                (cls.starts_at.is_(None)) | (cls.starts_at <= now),
                (cls.ends_at.is_(None)) | (cls.ends_at > now),
            )
        )
        return db.session.scalars(query).all()

    def flash_me(self):
        flash(self.message, self.level.name)
