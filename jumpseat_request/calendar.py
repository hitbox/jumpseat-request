import calendar

from jumpseat_request import settings

dayname = lambda day: calendar.day_name[day]

dayabbr = lambda day: calendar.day_abbr[day]

def build_calendar(year, today=None):
    """
    Build calendar data structure for a year for templates.
    """
    firstweekday = settings.firstweekday()
    if firstweekday is None:
        raise ValueError(f'JUMPSEAT_REQUEST_FIRSTWEEKDAY must be configured.')
    cal = calendar.Calendar(firstweekday=firstweekday)
    data = []
    for month in range(1, 13):
        dates = []
        for date in cal.itermonthdates(year, month):
            date_data = {
                'day': date.day,
                'date': date,
                'is_today': date == today,
            }
            dates.append(date_data)
        month_data = {
            'number': month,
            'name': calendar.month_name[month],
            'abbr': calendar.month_abbr[month],
            'dates': dates,
        }
        if month < 4:
            month_data.update({
                'weekdays': list(map(dayabbr, cal.iterweekdays())),
            })
        data.append(month_data)

    return data
