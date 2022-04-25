import os
import ee
import pandas as pd
from ee.geometry import Geometry

import logging
logger = logging.getLogger(__name__)

from datetime import date

def run(ids:list[str], google_points: Geometry, start_date: date, end_date: date, scale:int = 100, **kwargs) -> pd.DataFrame:
    """Collects land surface temperature"""
    elv = ee.Image('USGS/SRTMGL1_003')
    elv_features = elv.sample(google_points, scale).getInfo()['features']
    elvs = [ float(x.get('properties').get('elevation')) for x in elv_features ]

    ndvi_return = pd.DataFrame({
        'id': ids,
        'lst_day': elvs
    })

    return ndvi_return