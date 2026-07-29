from datetime import date
from datetime import datetime
from zoneinfo import ZoneInfo

class TimeZone:

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.zoneinfo = ZoneInfo(app.config.get('JUMPSEAT_REQUEST_TIMEZONE'))
        self.binds = app.config.get('JUMPSEAT_REQUEST_TIMEZONE_BINDS', {})
        self.timezones = {name: ZoneInfo(zonekey) for name, zonekey in self.binds.items()}

    def now(self):
        return datetime.now(tz=self.zoneinfo)

    def today(self):
        return datetime.now().date()

    def make_aware(self, dt):
        if dt.tzinfo is not None:
            raise ValueError(f'Expected naive datetime')
        return dt.replace(tzinfo=self.zoneinfo)
