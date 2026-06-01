import uuid

from jumpseat_request.extension import db

class JumpseatRequest(db.Model):
    """
    Jumpseat Request.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    employer_airline_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('airline.id'),
        comment = 'Airline employing the jump seat requester',
    )

    employer_airline = db.orm.relationship(
        'Airline',
    )

    flight_date = db.Column(
        db.Date,
        nullable = False,
        comment = 'Flight date in UTC (Zulu)',
    )

    approved_at = db.Column(
        db.DateTime(timezone=True),
        nullable = False,
        comment = 'UTC datetime of approval, null otherwise.',
    )

    denied_at = db.Column(
        db.DateTime(timezone=True),
        nullable = False,
        comment = 'UTC datetime of request denial othewise null.',
    )
