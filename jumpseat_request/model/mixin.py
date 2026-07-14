from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from jumpseat_request import settings
from jumpseat_request.extension import db
from jumpseat_request.extension import timezone

class ModelMixin:

    created_at = db.Column(
        db.DateTime(timezone=True),
        insert_default = timezone.now,
        nullable = False,
        info = {
            'ui_table': {
                'columnargs': {
                    'header': 'Created',
                },
            },
        },
    )

    @classmethod
    def criteria_for_created_at_age_seconds(cls, now):
        return db.func.extract('epoch', now - cls.created_at)

    @property
    def created_at_formatted(self):
        if self.created_at is None:
            return None
        fmt = settings.datetime_format()
        return self.created_at.strftime(fmt)

    @hybrid_property
    def created_at_age_seconds(self):
        if self.created_at is None:
            return None
        return (timezone.now() - self.created_at).total_seconds()

    @created_at_age_seconds.expression
    def created_at_age_seconds(cls):
        return cls.criteria_for_created_at_age_seconds(timezone.now())

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default = timezone.now,
        onupdate = timezone.now,
        nullable = True,
        info = {
            'ui_table': {
                'columnargs': {
                    'header': 'Upated',
                },
            },
        },
    )

    @classmethod
    def query_factory(cls):
        # QuerySelectField support mixin.
        # Confusingly it wants the instances *not* the query/select.
        return db.session.scalars(db.select(cls)).all()

    @classmethod
    def get_unique_by_attribute(cls, attrname, value, case_sensitive=False):
        attr = getattr(cls, attrname)

        if case_sensitive:
            cond = attr == value
        else:
            cond = attr.ilike(value)
        query = db.select(cls).where(cond)
        return db.session.scalars(query).one_or_none()

    @classmethod
    def name_for_template(cls):
        default = cls.__tablename__.title().replace('_', ' ')
        return getattr(cls, '__name_for_template__', default)
