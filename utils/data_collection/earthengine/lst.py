import os
import ee
from ee.geometry import Geometry

from datetime import date

def run(ids:list[str], google_points: Geometry, start_date: date, end_date: date, **kwargs):
    """Collects land surface temperature

    return