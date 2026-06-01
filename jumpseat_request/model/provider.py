import uuid

from jumpseat_request.extension import db

class Provider(db.Model):

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
