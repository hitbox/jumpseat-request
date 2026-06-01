import sqlalchemy as sa

from markupsafe import Markup

class Column:

    def __init__(self, attrname):
        self.attrname = attrname

    @classmethod
    def from_property(cls, prop):
        col = Column(key, is_hidden)
        return col

    def __str__(self):
        return self.attrname

    def get_value(self, instance):
        return getattr(instance, self.attrname)

    def __call__(self, obj):
        return self.get_value(obj)


class Table:

    def __init__(self, columns):
        self.columns = columns

    @classmethod
    def from_model(cls, model):
        mapper = sa.inspect(model)
        columns = []
        for key, prop in mapper.attrs.items():
            if not isinstance(prop, sa.orm.relationships.Relationship):
                is_hidden = prop.info.get('is_hidden', False)
                if not is_hidden:
                    col = Column(key)
                    columns.append(col)
        instance = cls(columns)
        return instance
