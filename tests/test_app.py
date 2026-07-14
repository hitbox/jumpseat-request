import os

import psycopg
import pytest

from psycopg import sql

from jumpseat_request.app import create_app
from jumpseat_request.extension import db as _db
from jumpseat_request.model import User
from jumpseat_request.model.user import UserState
from jumpseat_request.model.user import UserStateType
from jumpseat_request.seed import seed_database

@pytest.fixture
def app():
    test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.py')
    os.environ['JUMPSEAT_REQUEST_CONFIG'] = test_config_path
    app = create_app()
    yield app

@pytest.fixture
def db(app):
    with app.app_context():
        # delete all tables
        _db.create_all()
        seed_database()
        yield _db
        _db.session.rollback()
        _db.drop_all()

@pytest.fixture
def users(db):
    users = {
        'admin': User(
            email_address = 'admin@company.com',
            password_hash = 'password',
            is_admin = True,
        ),
        'user': User(
            email_address = 'user@company.com',
            password_hash = 'password',
        ),
        'reset_password_user': User(
            email_address = 'user-need-reset@company.com',
            password_hash = 'password',
            reset_password = True,
        ),
    }
    for user in users.values():
        db.session.add(user)
    db.session.commit()
    return users
