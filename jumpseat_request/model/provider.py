import uuid

from jumpseat_request.extension import db

from .mixin import ModelMixin

class Provider(db.Model, ModelMixin):

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
