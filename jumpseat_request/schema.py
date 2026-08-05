import marshmallow as mm

class LegQueryArgsSchema(mm.Schema):
    class Meta:
        # ignore extra arguments
        unknown = mm.EXCLUDE

    flight_number = mm.fields.Integer(data_key='fn_number')

    flight_datetime = mm.fields.DateTime(
        data_key = 'dep_sched_dt',
        format = 'iso',
    )

    scheduled_departure_airport = mm.fields.String(
        data_key = 'dep_ap_sched',
    )

    scheduled_arrival_airport = mm.fields.String(
        data_key = 'arr_ap_sched',
    )

    @mm.pre_load
    def handle_multidict(self, data, **kwargs):
        return {
            key: first_for_list(value)
            for key, value in data.items()
        }

def first_for_list(value):
    if isinstance(value, list):
        return value[0]
    else:
        return value
