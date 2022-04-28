import os
import ee
import pandas as pd
from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

from datetime import date

def run(ids:list[str], google_points: FeatureCollection, start_date: date, end_date: date, scale:int = 100, **kwargs) -> FeatureCollection:
    """Collects land surface temperature"""
    lst_raw = ee.ImageCollection('MODIS/006/MOD11A1')
    total_geometry = google_points.geometry()
    lst = lst_raw.filterDate(start_date, end_date).filterBounds(total_geometry)
    lst_day = lst.select('LST_Day_1km')
    lst_night = lst.select('LST_Night_1km')

    def custom_reducer(image):
        meanLst = image.reduceRegions(
            collection= google_points,
            reducer= ee.Reducer.mean(),
            scale= scale
         );

        meanLst_notnull = meanLst.filter(ee.Filter.notNull(['mean']))
        def mapfunction(feature):
            selection = feature.select(['mean'],['meanLST'])
            return selection.set({
                'imgID': image.id(),
                'date': image.date().format("yyyy-MM-dd HH:mm:ss.SSS")
            })

        return meanLst_notnull.map(mapfunction)

    lst_daymap = lst_day.map(custom_reducer).flatten().getInfo()
    lst_nightmap = lst_night.map(custom_reducer).flatten().getInfo()

    return {
        'day':lst_daymap,
        'night':lst_nightmap
    }