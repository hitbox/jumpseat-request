import uuid

from argon2 import exceptions as password_exceptions
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from jumpseat_request import settings
from jumpseat_request.extension import db
from jumpseat_request.extension import timezone
from jumpseat_request.frontend import yesno
from jumpseat_request.password import password_hasher

from .mixin import ModelMixin

class User(db.Model, UserMixin, ModelMixin):
    """
    User account.
    """

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
        info = {
            'is_hidden': True,
        },
    )

    email_address = db.Column(
        db.String,
        unique = True,
        nullable = False,
        info = {
            'blurb': 'Email address',
        }
    )

    @db.validates('email_address')
    def normalize_email_address(self, key, value):
        """
        Clear email verified if changed and normalize email
        address to lower-case.
        """
        return value.lower()

    email_verified_at = db.Column(
        db.DateTime(timezone=True),
        comment = 'The datetime the email address was verified',
        info = {
            'blurb': 'Datetime a secret token was verified from the inbox of the email.',
        }
    )

    @property
    def email_verified_at_formatted(self):
        if self.email_verified_at:
            return self.email_verified_at.strftime(settings.datetime_format())

    @hybrid_property
    def email_verified(self):
        return self.email_verified_at is not None

    @email_verified.setter
    def email_verified(self, value):
        self.email_verified_at = timezone.now()

    @email_verified.expression
    def email_verified(cls):
        return cls.email_verified.isnot(None)

    password_hash = db.Column(
        db.String,
        nullable = True, # allow external auth with null password hash
        comment = 'Password hash.',
        info = {
            'is_hidden': True,
        },
    )

    reset_password = db.Column(
        db.Boolean,
        nullable = False,
        default = False,
        info = {
            'blurb': 'Force account to change password.',
        },
    )

    @db.validates('password_hash')
    def validate_password(self, key, value):
        """
        Hash password text.
        """
        return password_hasher.hash(value)

    employee = db.orm.relationship(
        'Employee',
        back_populates = 'user',
        uselist = False,
        info = {
            'blurb': 'Employee associated with account.'
        }
    )

    is_active = db.Column(
        db.Boolean,
        nullable = False,
        default = True,
        comment = 'Active user account can login',
        info = {
            'html': {
                'columnargs': {
                    'cast': yesno,
                }
            },
            'blurb': 'Account can be used to login.',
        }
    )

    is_decider = db.Column(
        db.Boolean,
        nullable = False,
        default = False,
        info = {
            'html': {
                'columnargs': {
                    'cast': yesno,
                }
            },
            'blurb': 'Account can approve or deny requests.',
        }
    )

    is_admin = db.Column(
        db.Boolean,
        nullable = False,
        default = False,
        info = {
            'blurb': 'Account can access admin pages.',
            'html': {
                'columnargs': {
                    'cast': yesno,
                }
            }
        }
    )

    jumpseat_requests = db.orm.relationship(
        'JumpseatRequest',
        foreign_keys = 'JumpseatRequest.request_by_user_id',
        back_populates = 'request_by',
        info = {
            'is_hidden': True,
        }
    )

    is_guest = db.Column(
        db.Boolean,
        default = False,
        nullable = False,
    )

    def verify_email_html(self):
        html = [
            f'<a href="">Send verification email.</a>'
        ]

    def as_choice_tuple(self):
        return (self.id, self.email_address)

    @classmethod
    def by_email(cls, email):
        """
        Case-insensitive lookup user object by email address.
        """
        if isinstance(email, str):
            email = email.lower()

        query = db.select(cls).where(cls.email_address == email)
        return db.session.scalars(query).one_or_none()

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

    @classmethod
    def choices(cls, include_none=True):
        user_query = db.select(cls).where(cls.employee == None)
        user_choices = [('', '(None)')]
        user_choices.extend([
            user.as_choice_tuple()
            for user in db.session.scalars(user_query)
        ])
        return user_choices

    def confirm_email(self):
        self.email_verified_at = timezone.now()
        self.is_active = True

    @property
    def best_show_name(self):
        if self.email_address:
            return self.email_address
