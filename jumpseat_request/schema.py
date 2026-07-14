from marshmallow import Schema
from marshmallow import fields

from .settings import date_format

class AirlineSchema(Schema):

    id = fields.UUID(required=True)
    iata_code = fields.String()
    icao_code = fields.String()


class EmployeeSchema(Schema):

    airline = fields.Nested(AirlineSchema)
    employee_number = fields.String()
    name = fields.String()
    email_address = fields.String(required=True)
    phone = fields.String(required=True)


class JumpseatRequestDataSchema(Schema):

    flight_date = fields.Date()
    flight_number = fields.String()

    employee = fields.Nested(EmployeeSchema)
