import smtplib

class SMTP:

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.smtp_args = app.config.get('JUMPSEAT_REQUEST_SMTP')

    def send_message(self, message):
        with smtplib.SMTP(**self.smtp_args) as smtp:
            smtp.send_message(message)
