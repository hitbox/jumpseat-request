import uuid

from jumpseat_request.extension import db

class Employee(db.Model):
    """
    An employee
    """

    __tableargs__ = (
        # unique employee for each airline
        db.UniqueConstraint('airline_id', 'employee_number')
    )

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    airline_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('airline.id'),
        comment = 'Airline employing the jump seat requester',
    )

    airline = db.orm.relationship(
        'Airline',
    )

    employee_number = db.Column(
        db.String,
        nullable = False,
    )

    contact_methods = db.orm.relationship(
        'ContactMethod',
        back_populates = 'employee',
        cascade = 'all, delete-orphan',
    )
