from jumpseat_request.db_compat import trunc_date
from jumpseat_request.extension import db
from jumpseat_request.model import Leg
from jumpseat_request.settings import scheduled_flight_carrier

# subquery to eliminate leg_no causing very many duplicates (since we only care
# about flight number, datetime, and carrier).
ranked_legs = (
    db.select(
        Leg,
        db.func.row_number().over(
            partition_by = (
                Leg.fn_carrier,
                Leg.fn_number,
                trunc_date(Leg.dep_sched_dt).label('dep_sched_date'),
            ),
            order_by = Leg.leg_no.desc(),
        )
        .label('rownumber')
    )
)

ranked_legs_sq = ranked_legs.subquery()

LegRanked = db.aliased(Leg, ranked_legs_sq)

newest_leg_scheduled_flights = (
    db.select(LegRanked)
    .where(
        ranked_legs_sq.c.rownumber == 1,
    )
)

newest_leg_subquey = newest_leg_scheduled_flights.subquery()

counts_by_date = (
    db.select(
        newest_leg_subquey.c.dep_sched_dt,
        db.func.count().label("count")
    )
    .group_by(newest_leg_subquey.c.dep_sched_dt)
    .order_by(newest_leg_subquey.c.dep_sched_dt)
)

def all_for_date_query(date):
    query = (
        db.select(LegRanked)
        .where(
            ranked_legs_sq.c.rownumber == 1,
            trunc_date(ranked_legs_sq.c.dep_sched_dt) == date,
            ranked_legs_sq.c.fn_carrier == scheduled_flight_carrier().iata_code,
        )
    )
    return query

def counts_after_date(date):
    query = (
        db.select(
            trunc_date(ranked_legs.c.dep_sched_dt).label('date'),
            db.func.count().label('count'),
        )
        .where(
            ranked_legs.c.rownumber == 1, # deduplicate from subquery
            ranked_legs.c.dep_sched_dt >= date,
            ranked_legs.c.fn_carrier == scheduled_flight_carrier().iata_code,
        )
        .group_by(
            trunc_date(ranked_legs.c.dep_sched_dt),
        )
        .order_by(
            trunc_date(ranked_legs.c.dep_sched_dt),
        )
    )
    return query
