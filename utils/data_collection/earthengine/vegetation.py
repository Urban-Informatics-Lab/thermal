import ee
import pandas as pd
from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

from datetime import date

def run(ids:list[str], google_points: FeatureCollection, start_date: date, end_date: date, scale:int = 100, **kwargs) -> FeatureCollection:
    """Collects historical vegetation around this point"""
    l8 = ee.ImageCollection("LANDSAT/LC08/C01/T1_8DAY_EVI")
    total_geometry = google_points.geometry()
    l8_filtered = l8.filterDate(start_date, end_date).filterBounds(total_geometry)
    evi = l8_filtered.select('EVI')

    def custom_reducer(image):
        sumEVI = image.reduceRegions(
            collection= google_points,
            reducer= ee.Reducer.sum(),
            scale= scale
         );

        sumEVI_notnull = sumEVI.filter(ee.Filter.notNull(['sum']))
        def mapfunction(feature):
            selection = feature.select(['sum'],['sumEVI'])
            return selection.set({
                'imgID': image.id(),
                'date': image.date()
            })

        return sumEVI_notnull.map(mapfunction)

    returning_value = evi.map(custom_reducer).flatten()

    # would be really neat if we could just kind of chain these feature collections together
    return returning_value.getInfo()