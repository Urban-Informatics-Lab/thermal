import os
import ee
import pandas as pd
from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

from datetime import date

# def run(ids:list[str], google_points: Geometry, start_date: date, end_date: date, scale:int = 100, **kwargs) -> pd.DataFrame:
#     """Collects land surface temperature"""
#     elv = ee.Image('USGS/SRTMGL1_003')
#     elv_features = elv.sample(google_points, scale).getInfo()['features']
#     elvs = [ float(x['properties']['elevation']) for x in sorted(elv_features, key=lambda d: d['id']) ]

#     elv_return = pd.DataFrame({
#         'id': ids,
#         'elv': elvs
#     })

#     return elv_return

def run(ids:list[str], google_points: FeatureCollection, start_date: date, end_date: date, scale:int = 100, **kwargs) -> FeatureCollection:
    """Collects historical vegetation around this point"""
    elv = ee.Image('USGS/SRTMGL1_003')
    return elv.reduceRegions(
        collection= google_points,
        reducer= ee.Reducer.mean(),
        scale= 30
    ).getInfo()