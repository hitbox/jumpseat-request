from jumpseat_request.extension import db
from jumpseat_request.model import Leg

ranked_legs = (
    db.select(
        Leg,
        db.func.row_number().over(
            partition_by = (
                Leg.fn_carrier,
                Leg.fn_number,
                db.func.trunc(Leg.dep_sched_dt).label('dep_sched_date'),
            ),
            order_by = Leg.leg_no.desc(),
        )
        .label('rownumber')
    )
).subquery()

LegRanked = db.aliased(Leg, ranked_legs)

newest_leg_scheduled_flights = (
    db.select(LegRanked)
    .where(
        ranked_legs.c.rownumber == 1,
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
