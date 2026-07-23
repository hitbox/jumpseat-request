from jumpseat_request.extension import db
from jumpseat_request.model import Leg

ranked_legs = (
    db.select(
        Leg,
        db.func.row_number().over(
            partition_by = (
                Leg.fn_carrier,
                Leg.fn_number,
                Leg.dep_sched_dt,
            ),
            order_by = Leg.leg_no,
        )
        .label('rn')
    )
).subquery()

LegRanked = db.aliased(Leg, ranked_legs)

newest_leg_scheduled_flights = (
    db.select(LegRanked)
    .where(
        ranked_legs.c.rn == 1,
    )
)
