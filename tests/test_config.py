# test_config.py
TESTING = True
SECRET_KEY = 'test-secret'

WTF_CSRF_ENABLED = False

TEST_DB_NAME = 'test_jumpseat_request'
SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg://localhost/{TEST_DB_NAME}'

JUMPSEAT_REQUEST_SHOW_AIRLINE_CODE = 'icao_code'
JUMPSEAT_REQUEST_TIMEZONE = 'America/New_York'

# flask_smtp — probably needs these even if not sending in tests
SMTP_HOST = 'localhost'
SMTP_PORT = 25

# flask_timezone
TIMEZONE = 'UTC'

#PREFIX_MIDDLEWARE_PREFIX = '/jumpseat-request'

JUMPSEAT_REQUEST_FROM_ADDRESS = 'carl.harris@company.com'

JUMPSEAT_REQUEST_DATETIME_FORMAT = '%d%b%y %H:%M:%S %p'
JUMPSEAT_REQUEST_DATE_FORMAT = '%d%b%y'
