import uuid

from argon2 import PasswordHasher
from argon2 import exceptions as password_exceptions
from flask_login import UserMixin

from jumpseat_request.extension import db

password_hasher = PasswordHasher()

class User(db.Model, UserMixin):
    """
    App specific user.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    username = db.Column(
        db.String,
        unique = True,
        nullable = False,
    )

    @db.orm.validates('username')
    def validate_username(self, key, value):
        """
        Require username to be truthy to catch empty string.
        """
        if not value or not value.strip():
            raise ValueError(f'Invalid username {value}')
        return value

    password_hash = db.Column(
        db.String,
        nullable = True, # allow external auth with null password hash
        comment = 'Password hash.',
        info = {
            'is_hidden': True,
        },
    )

    is_active = db.Column(
        db.Boolean,
        nullable = False,
        default = True,
        comment = 'Active user account can login',
    )

    is_admin = db.Column(
        db.Boolean,
        nullable = False,
        default = False,
    )

    @classmethod
    def by_username(cls, username):
        query = db.select(cls).where(cls.username == username)
        return db.session.scalars(query).one_or_none()

    @classmethod
    def create(cls, username, password_text, is_admin=False, is_active=True):
        """
        Create a new user account.
        """
        user = cls.by_username(username)
        if user is not None:
            raise ValueError(f'Username {username!r} already exists')
        user = cls(
            username = username,
            password_hash = password_hasher.hash(password_text),
            is_admin = is_admin,
            is_active = is_active,
        )
        return user

    def check_password(self, password_text):
        """
        Verify password string against stored hashed.
        """
        if not self.is_active:
            return False
        
        try:
            return password_hasher.verify(self.password_hash, password_text)
        except password_exceptions.VerifyMismatchError:
            return False
