import uuid

from jumpseat_request.extension import db

from .mixin import ModelMixin

class Rank(db.Model, ModelMixin):
    """
    Employee rank.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    code = db.Column(
        db.String,
        nullable = False,
        index = True,
    )

    @db.validates('code')
    def validate_code(self, key, value):
        return value.upper()

    name = db.Column(
        db.String,
        nullable = False,
    )

    @classmethod
    def by_code(cls, rank_code):
        query = (
            db.select(Rank)
            .where(Rank.code == rank_code)
        )
        return db.session.scalars(query).one_or_none()

    @classmethod
    def pagination_getter(cls):
        """
        Rank objects sorted by code.
        """
        query = (
            db.select(cls)
            .order_by(cls.code)
        )
        return db.paginate(query)
