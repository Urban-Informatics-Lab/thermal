import datetime

from datetime import date
from dateutil.rrule import rrule, MONTHLY

def datelist(start_date: date, end_date: date) -> list:
    """build a date list of each month we want to collect data for"""
    dates = [dt for dt in rrule(MONTHLY, dtstart=start_date, until=end_date)]
    dates.append(end_date)
    return dates