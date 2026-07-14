import uuid

from markupsafe import Markup

from jumpseat_request.extension import db

from htmlkit.lists import unordered_list

from .mixin import ModelMixin

def _nice_contact_methods(contact_methods):
    html = ['<div class="contacts">']
    for contact_method in contact_methods:
        type_class = contact_method.type_object.name.lower()
        type_text = contact_method.type_object 
        html.append(
            f'<div class="contact-type {type_class}">{type_text}</div>'
            f'<div class="contact-value">{ contact_method.value }</div>'
            f'<div clsas="contact-notes">{ contact_method.notes }</div>'
        )

    html.append('</div>')

    return Markup(''.join(html))

class Employee(db.Model, ModelMixin):
    """
    Employee information that can be linked to a user account.
    """

    __table_args__ = (
        # unique employee for each airline
        db.UniqueConstraint('airline_id', 'employee_number'),
    )

    __html_column_order__ = [
        'name',
        'employee_number',
        'airline',
        'user',
    ]

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    airline_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('airline.id'),
        comment = 'Airline employing the jump seat requester',
    )

    airline = db.orm.relationship(
        'Airline',
        info = {
            'blurb': 'Employee\'s airline--their employer.',
        },
    )

    employee_number = db.Column(
        db.String,
        nullable = False,
        unique = True,
        info = {
            'header': 'Employee #',
            'blurb': 'Employee number as given by their employer.',
        }
    )

    name = db.Column(
        db.String,
        unique = True,
        nullable = True,
        info = {
            'ui_table': {
                'columnargs': {
                    'header': 'Name',
                },
            },
            'blurb': 'Employee\'s real name.',
        },
    )

    phone = db.Column(
        db.String,
        nullable = True,
        info = {
            'ui_table': {
                'columnargs': {
                    'header': 'Name',
                },
            },
        },
    )

    user_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('user.id'),
    )

    user = db.orm.relationship(
        'User',
        back_populates = 'employee',
        info = {
            'blurb': 'Associated user account.',
        },
    )

    def as_choice_tuple(self):
        return (self.id, str(self))

    def __str__(self):
        return self.employee_number

    def try_lookup(self, data):
        employee_number = data.get('employee_number')
        employee_name = data.get('name')
