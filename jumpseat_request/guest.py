import uuid

from flask import session as flask_session
from flask_login import current_user

from jumpseat_request.extension import db
from jumpseat_request.model import User

def get_current_user_or_create_guest(email_address=None):
    """
    Return current_user if authenticated otherwise return guest user from
    session, creating one if an email is given.
    """
    user = None
    if current_user.is_authenticated:
        user = current_user
    else:
        if 'guest_id' in flask_session:
            user = db.session.get(User, {'id': flask_session['guest_id']})
            if user:
                user.is_guest = True
                # Force the guest account email address.
                user.email_address = email_address

        # guest_id in session might be invalid, just make a user if still none.
        if user is None:
            if email_address is None:
                raise ValueError(f'email_address is required for no authenticated user')

            user = User(
                email_address = email_address,
                is_guest = True,
            )
            db.session.add(user)
            db.session.flush()
            flask_session['guest_id'] = user.id

    if (
        email_address is not None
        and
        user
        and user.email_address != email_address
    ):
        raise ValueError(
            f'Mismatched email: {user.email_address=} and {email_address=}'
        )

    return user
