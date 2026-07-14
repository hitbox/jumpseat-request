from flask import request

from jumpseat_request import signal
from jumpseat_request.form import EditJumpseatRequestForm
from jumpseat_request.form import NewJumpseatRequestForm
from jumpseat_request.guest import get_current_user_or_create_guest
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.schema import JumpseatRequestDataSchema
from jumpseat_request.extension import db

def populate_jumpseat_object(form, instance):
    request_data_schema = JumpseatRequestDataSchema()
    form_data = form.data
    email = form.employee.email_address.data

    json_data = request_data_schema.dump(form_data)
    request_by = get_current_user_or_create_guest(email=email)

    # Populate new object
    instance.data = json_data
    instance.request_by = request_by

    # Flush for PK--subscribers will need it.
    db.session.flush()

    return

    # Fire signals
    signal.jumpseat_request_created.send(
        request.endpoint, # sender must be first positional arg
        signal = signal.jumpseat_request_created,
        jumpseat_request = instance,
    )
    db.session.commit()

def create_new_jumpseat_request(form, instance=None):
    form_classes = (EditJumpseatRequestForm, NewJumpseatRequestForm)
    assert isinstance(form, form_classes), f'{type(form)=} must in {form_classes=}'

    if isinstance(form, NewJumpseatRequestForm) and instance is None:
        raise ValueError(f'instance must be given for NewJumpseatRequestForm')

    request_data_schema = JumpseatRequestDataSchema()
    form_data = form.data
    email = form.employee.email_address.data

    json_data = request_data_schema.dump(form_data)
    request_by = get_current_user_or_create_guest(email=email)

    # Populate new object
    instance.data = json_data
    instance.request_by = request_by

    # Flush for PK--subscribers will need it.
    db.session.flush()

    # Fire signals
    signal.jumpseat_request_created.send(
        request.endpoint, # sender must be first positional arg
        signal = signal.jumpseat_request_created,
        jumpseat_request = instance,
    )
    db.session.commit()
