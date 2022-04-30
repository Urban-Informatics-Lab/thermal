import os
import ee
import pandas as pd
import geemap
from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

from datetime import date

def run(google_points: FeatureCollection, start_date: date, end_date: date, scale:int = 100, **kwargs) -> FeatureCollection:
    """Collects land surface temperature"""
    lst_raw = ee.ImageCollection('MODIS/006/MOD11A1')
    total_geometry = google_points.geometry()
    lst = lst_raw.filterDate(start_date, end_date).filterBounds(total_geometry)

    def custom_reducer(image):
        def image_properties(feature):
            extra_info = ee.Feature(None, {
                'imgID': image.id(),
                'date': image.date().format("YYYY-MM-dd HH:mm:ss")
                }).copyProperties(feature)
            return extra_info

        lst_reduced = image.reduceRegions(
            collection= google_points,
            reducer= ee.Reducer.mean(),
            scale= scale
         ).map(image_properties)
         
        return lst_reduced

    returning = geemap.ee_to_geopandas(lst.map(custom_reducer).flatten())
    return returning