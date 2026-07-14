from collections import OrderedDict

class OrderedFieldsMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self, '__fields__'):
            # Apply explicit ordering to fields by dict key name.
            ordering = self.__fields__

            def key(item):
                key, field = item
                if key in ordering:
                    return ordering.index(key)
                else:
                    return float('inf')

            self._fields = OrderedDict(sorted(self._fields.items(), key=key))
