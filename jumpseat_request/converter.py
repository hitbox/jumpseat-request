from datetime import datetime

from werkzeug.routing import BaseConverter

class DateConverter(BaseConverter):
    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        return datetime.strptime(value, "%Y-%m-%d").date()


def init_app(app):
    app.url_map.converters["date"] = DateConverter
