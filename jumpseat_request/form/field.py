from wtforms import FieldList

class DynamicFieldList(FieldList):
    """
    Subclass FieldList to detect and render with special template.
    """
