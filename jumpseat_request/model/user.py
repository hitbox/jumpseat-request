import uuid

from enum import Enum

from argon2 import exceptions as password_exceptions
from flask import current_app
from flask import session as flask_session
from flask_login import AnonymousUserMixin
from flask_login import UserMixin
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy.ext.hybrid import hybrid_property

from jumpseat_request.extension import db
from jumpseat_request.extension import login_manager
from jumpseat_request.extension import timezone
from jumpseat_request.frontend import yesno
from jumpseat_request.password import password_hasher
from jumpseat_request.secret import six_digit_code

from .mixin import ModelMixin

class User(db.Model, UserMixin, ModelMixin):
    """
    User account.
    """

    __html_column_order__ = [
        'email_address',
        'is_active',
        'is_admin',
        'employee',
    ]

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
    )

    @db.validates('email_address')
    def clear_verified(self, key, value):
        """
        Clear email verified if changed.
        """
        if self.email_address and self.email_address != value:
            self.email_verified_at = None
        return value

    email_verified_at = db.Column(
        db.DateTime(timezone=True),
        comment = 'The datetime the email address was verified',
    )

    @hybrid_property
    def email_verified(self):
        return self.email_verified_at is not None

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
