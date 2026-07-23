import math

import sqlalchemy as sa

from markupsafe import Markup

class Column:

    def __init__(self, attrname, header=None, cast=None, th_attrs=None):
        self.attrname = attrname
        self.header = header
        self.cast = cast
        self.th_attrs = th_attrs

    def __str__(self):
        return self.attrname

    def get_value(self, instance):
        value = deepgetattr(instance, self.attrname)
        if callable(value):
            value = value()
        if callable(self.cast):
            value = self.cast(instance, value)
        return value

    def __call__(self, obj):
        return self.get_value(obj)


class Table:

    def __init__(self, columns, description=None):
        self.columns = columns
        self.description = description

    @classmethod
    def from_model(cls, model, include_fk=False, include_pk=False):
        table_columns = []

        def should_include(prop):
            info = get_ui_table_args(prop)
            if info:
                is_hidden = info.get('is_hidden', False)
            else:
                is_hidden = False
            if hasattr(prop, 'columns'):
                is_pk = any(column.primary_key for column in prop.columns)
                is_fk = any(bool(column.foreign_keys) for column in prop.columns)
                # overwrite is_hidden for any truthy info dicts
                for column in prop.columns:
                    if 'is_hidden' in column.info:
                        is_hidden = True
            else:
                is_pk = False
                is_fk = False

            if is_hidden:
                return False

            if is_pk and not include_pk:
                return False

            if is_fk and not include_fk:
                return False

            return True

        def get_ui_table_args(prop):
            info = {}
            if 'ui_table' in prop.info:
                info.update(prop.info['ui_table'])
            return info

        def get_column_args(prop):
            ui_table = get_ui_table_args(prop)
            return ui_table.get('columnargs', {})

        def titlize(attrname):
            return ' '.join(s.title() for s in attrname.split('_'))

        mapper = sa.inspect(model)
        for key, prop in mapper.attrs.items():
            if should_include(prop):
                header = None
                column_args = get_column_args(prop)
                column_args.setdefault('attrname', prop.key)
                column_args.setdefault('header', titlize(prop.key))
                col = Column(**column_args)
                table_columns.append(col)

        # sort columns
        if hasattr(model, '__html_column_order__'):
            def key(column):
                if column.attrname in model.__html_column_order__:
                    return model.__html_column_order__.index(column.attrname)
                else:
                    return math.inf
            table_columns = sorted(table_columns, key=key)

        instance = cls(table_columns)
        return instance

def deepgetattr(obj, name):
    for name in name.split('.'):
        obj = getattr(obj, name)
        if obj is None:
            return
    return obj
