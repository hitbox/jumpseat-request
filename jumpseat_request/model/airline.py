import uuid

from argon2 import PasswordHasher
from argon2 import exceptions as password_exceptions
from flask_login import UserMixin

from jumpseat_request.extension import db
from jumpseat_request.settings import airline_label_attribute

from .mixin import ModelMixin

password_hasher = PasswordHasher()

class Airline(db.Model, ModelMixin):
    """
    An Airline that appears as the employer of a jumpseat requester.
    """

    # kwargs to pluggable views
    __admin__ = {
        'edit': {
            'form_class': 'EditAirlineForm',
        },
        'table': {
        },
    }

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    iata_code = db.Column(
        db.String,
        nullable = False,
        unique = True,
    )

    icao_code = db.Column(
        db.String,
        nullable = False,
        unique = True,
    )

    def __str__(self):
        return self.icao_code

    def as_choice_tuple(self):
        return (self.id, str(self.icao_code))

    @property
    def configured_display_code(self):
        attr = airline_label_attribute()
        return getattr(self, attr)
