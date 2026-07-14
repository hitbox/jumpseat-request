from datetime import datetime
from zoneinfo import ZoneInfo

class TimeZone:

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.zoneinfo = ZoneInfo(app.config.get('JUMPSEAT_REQUEST_TIMEZONE'))

    def now(self):
        return datetime.now(tz=self.zoneinfo)
