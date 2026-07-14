from jumpseat_request.extension import db
from jumpseat_request.model import Airline
from jumpseat_request.model import AnnouncementLevel
from jumpseat_request.model import AnnouncementLevelType
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import NotificationRecipient
from jumpseat_request.model import NotificationRule
from jumpseat_request.model import Provider
from jumpseat_request.model import User

def seed_database():
    """
    Seed database with data absolutely necessary for a function web app.
    """
    # These are intended to be the database data that is at least fairly
    # business agnostic and the app will not work without.

    # Check before add for tests.
    query = db.select(Provider).where(Provider.name == 'okta')
    if not db.session.scalars(query).one_or_none():
        db.session.add(Provider(name='okta'))

    airlines = [
        ('GB', 'ABX'),
        ('8C', 'ATN'),
    ]
    for iata_code, icao_code in airlines:
        query = db.select(Airline).where(Airline.iata_code == iata_code)
        exists = db.session.scalars(query).one_or_none()
        if not exists:
            db.session.add(Airline(iata_code=iata_code, icao_code=icao_code),)

    # Mirror announcement levels to database
    for member in AnnouncementLevelType:
        query = (
            db.select(AnnouncementLevel)
            .where(AnnouncementLevel.name == member.name)
        )
        instance = db.session.scalars(query).one_or_none()
        if instance is None:
            instance = AnnouncementLevel(name=member.name)
            db.session.add(instance)

    db.session.commit()
