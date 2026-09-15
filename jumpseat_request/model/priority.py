import uuid

from flask import current_app
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from jumpseat_request import settings
from jumpseat_request.extension import db
from jumpseat_request.extension import timezone
from jumpseat_request.signal import jumpseat_request_decided
from jumpseat_request.signal import jumpseat_request_escalate

from .mixin import ModelMixin
from .rank import Rank
from .user import User

class JumpseatRequestPriority(db.Model):
    """
    User submitted request for jumpseat on a flight.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    name = db.Column(
        db.String,
        unique = True,
        nullable = False,
    )

    requests = db.orm.relationship(
        'JumpseatRequest',
        back_populates = 'priority',
    )
