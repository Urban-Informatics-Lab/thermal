import os
import ee
from datetime import date

def run(start_date: date, end_date: date, **kwargs):
    """Collects land surface temperature

    return