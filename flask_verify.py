import smtplib

from itsdangerous import BadSignature
from itsdangerous import SignatureExpired
from itsdangerous import URLSafeTimedSerializer

class TimedToken:
    """
    Generate and verify timed tokens for verification.
    """

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        self.max_age = app.config.get('TOKEN_MAX_AGE')
        self.salt = app.config.get('TOKEN_SALT')

    def create_token(self, email, user_id, jumpseat_request_id):
        payload = {
            'email': email,
            'user_id': user_id,
            'jumpseat_request_id': jumpseat_request_id,
        }
        token = self.serializer.dumps(payload, salt=self.salt)
        return token

    def load_token(self, token):
        try:
            data = self.serializer.loads(token, salt=self.salt, max_age=self.max_age)
        except SignatureExpired:
            return (None, 'token expired')
        except BadSignature:
            return (None, 'token invalid')
        return (data, None)
