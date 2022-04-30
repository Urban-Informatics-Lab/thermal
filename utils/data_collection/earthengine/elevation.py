import os
import ee
import pandas as pd
import geemap
from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

from datetime import date

def run(google_points: FeatureCollection, start_date: date, end_date: date, scale:int = 100, **kwargs) -> FeatureCollection:
    """Collects historical vegetation around this point"""
    elv = ee.Image('USGS/SRTMGL1_003')
    reduced = elv.reduceRegions(
        collection= google_points,
        reducer= ee.Reducer.mean(),
        scale= 30
    )

    return geemap.ee_to_pandas(reduced)