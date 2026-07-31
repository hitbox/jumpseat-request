import uuid

from jumpseat_request.extension import db

from .mixin import ModelMixin

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
        from jumpseat_request.settings import airline_label_attribute
        attr = airline_label_attribute()
        return getattr(self, attr)

    @classmethod
    def by_iata(cls, iata_code):
        return db.session.scalars(db.select(cls).where(cls.iata_code == iata_code)).one()

    @classmethod
    def by_icao(cls, icao_code):
        return db.session.scalars(db.select(cls).where(cls.icao_code == icao_code)).one()

    @classmethod
    def query_factory(cls):
        # QuerySelectField support mixin.
        return db.session.scalars(db.select(cls).order_by(cls.icao_code)).all()
