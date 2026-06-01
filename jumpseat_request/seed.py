from jumpseat_request.extension import db
from jumpseat_request.model import Airline
from jumpseat_request.model import ContactMethod
from jumpseat_request.model import ContactMethodType
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import Provider
from jumpseat_request.model import ContactType
from jumpseat_request.model import User

def seed_database():
    """
    Seed database with data absolutely necessary for a function web app.
    """
    db.session.add(Provider(name='okta'))

    # Mirror enum to database
    for member in ContactType:
        query = (
            db.select(ContactMethodType)
            .where(ContactMethodType.name == member.name)
        )
        instance = db.session.scalars(query).one_or_none()
        if not instance:
            instance = ContactMethodType(name=member.name)
            db.session.add(instance)
    db.session.add(Airline(iata_code='GB', icao_code='ABX'),)
    db.session.add(Airline(iata_code='8C', icao_code='ATN'),)
    db.session.commit()
