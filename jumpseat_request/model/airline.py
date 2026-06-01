import uuid

from argon2 import PasswordHasher
from argon2 import exceptions as password_exceptions
from flask_login import UserMixin

from jumpseat_request.extension import db

password_hasher = PasswordHasher()

class Airline(db.Model):
    """
    Airline
    """

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
