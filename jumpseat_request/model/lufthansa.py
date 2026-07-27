from datetime import datetime
from datetime import timedelta

from sqlalchemy.ext.hybrid import Comparator
from sqlalchemy.ext.hybrid import hybrid_property

from jumpseat_request import settings
from jumpseat_request.db_compat import trunc_date
from jumpseat_request.extension import db


class DateComparator(Comparator):
    def __eq__(self, other):
        start = datetime.combine(other, datetime.min.time())
        end = start + timedelta(days=1)

        return and_(
            self.__clause_element__() >= start,
            self.__clause_element__() < end,
        )


class Leg(db.Model):
    """
    User account.
    """

    __bind_key__ = 'lsyrept'

    __tablename__ = 'LEG'

    __table_args__ = {
        'schema': 'schedops',
    }

    what_if = db.Column(
        db.String(20),
        primary_key = True,
    )

    leg_no = db.Column(
        db.Integer,
        primary_key = True,
    )

    fn_carrier = db.Column(
        db.String(3),
        nullable = False,
        info = {
            'comment': 'Three letter ICAO Carrier/Airline code.'
        }
    )

    fn_number = db.Column(
        db.Integer,
        nullable = False,
        info = {
            'comment': 'Integer flight number.',
        }
    )

    fn_suffix = db.Column(
        db.String(1),
        nullable = False,
    )

    day_of_origin = db.Column(
        db.DateTime,
        index = True,
    )

    dep_sched_dt = db.Column(
        db.DateTime,
        index = True,
    )

    @hybrid_property
    def dep_sched_date(self):
        if self.dep_sched_dt:
            return self.dep_sched_dt.date()

    @dep_sched_date.expression
    def dep_sched_date(cls):
        return trunc_date(cls.dep_sched_dt)

    @dep_sched_date.comparator
    def dep_sched_date(cls):
        return DateComparator(cls.dep_sched_dt)


    dep_ap_sched = db.Column(
        db.String(3),
        nullable = False,
        info = {
            'comment': 'Scheduled departure airport.'
        },
    )

    arr_ap_sched = db.Column(
        db.String(3),
        nullable = False,
        info = {
            'comment': 'Scheduled arrival airport.'
        },
    )

    @property
    def flight_number(self):
        string = str(self.fn_number)
        if self.fn_suffix:
            string += self.fn_suffix
        return string

    @property
    def dep_sched_date(self):
        if self.dep_sched_dt:
            return self.dep_sched_dt.date()

    @property
    def day_of_origin_formatted(self):
        if self.day_of_origin:
            return self.day_of_origin.strftime(settings.datetime_format())

    @property
    def dep_sched_dt_formatted(self):
        if self.dep_sched_dt:
            return self.dep_sched_dt.strftime(settings.datetime_format())

    @property
    def dep_sched_time(self):
        if self.dep_sched_dt:
            return self.dep_sched_dt.time()

    @property
    def dep_sched_time_formatted(self):
        if self.dep_sched_dt:
            return self.dep_sched_dt.strtime(settings.time_format())

    @classmethod
    def all_for_date(cls, date):
        """
        List of all Leg objects for given date.
        """
        from jumpseat_request.query import LegRanked
        from jumpseat_request.query import newest_leg_scheduled_flights
        from jumpseat_request.query import ranked_legs
        from jumpseat_request.settings import scheduled_flight_carrier

        scheduled_flight_carrier = scheduled_flight_carrier()
        query = (
            db.select(LegRanked)
            .where(
                ranked_legs.c.rownumber == 1,
                trunc_date(ranked_legs.c.dep_sched_dt) == date,
                ranked_legs.c.fn_carrier == scheduled_flight_carrier.iata_code,
            )
        )
        return db.session.scalars(query).all()
