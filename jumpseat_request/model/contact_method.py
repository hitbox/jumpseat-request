import uuid

from enum import Enum

from jumpseat_request.extension import db

class ContactType(Enum):
    """
    Python-side values for types of contact methods.
    """

    PHONE = 'phone'
    EMAIL = 'email'


class ContactMethodType(db.Model):
    """
    A way to contact a person.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    name = db.Column(
        db.String,
        nullable = False,
        unique = True,
    )

    def as_type(self):
        return ContactType(self.name)


class ContactMethod(db.Model):
    """
    Specific contact for an employee.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    employee_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('employee.id'),
        nullable = False,
    )

    employee = db.orm.relationship(
        'Employee',
        back_populates = 'contact_methods',
    )

    type_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('contact_method_type.id'),
        nullable = False,
    )

    type_object = db.orm.relationship(
        'ContactMethodType',
    )

    value = db.Column(
        db.String,
        nullable = False,
    )

    notes = db.Column(
        db.String,
        nullable = True,
        comment = 'User provided notes/instructions for this contact method.',
    )
