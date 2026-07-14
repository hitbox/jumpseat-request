from jumpseat_request.extension import db

from .mixin import ModelMixin

class Identity(db.Model, ModelMixin):
    """
    Identity from external authorization provider.
    """

    id = db.Column(
        db.Integer(),
        primary_key = True,
    )

    provider_id = db.Column(
        db.UUID,
        db.ForeignKey('provider.id'),
        nullable = False,
    )
