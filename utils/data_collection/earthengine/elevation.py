import os
import ee
import pandas as pd
import geemap
from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

from datetime import date

def run(google_points: FeatureCollection, start_date: date, end_date: date, scale:int = 100, **kwargs) -> dict:
    """Collects historical vegetation around this point"""
    elv = ee.Image('USGS/SRTMGL1_003')
    returning_region = elv.reduceRegions(
        collection= google_points,
        reducer= ee.Reducer.mean().setOutputs(["elevation"]),
        scale= 30
    ).map(lambda feature: feature.setGeometry(None))

    return {
        "selectors":["elevation"],
        "collection":returning_region
    }