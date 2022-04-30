import ee
import pandas as pd
import geemap
from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

from datetime import date

def addNDVI(image):
    return image.addBands(image.normalizedDifference(['B8', 'B4']).rename('ndvi'))

def run(google_points: FeatureCollection, start_date: date, end_date: date, scale:int = 100, **kwargs) -> FeatureCollection:
    """Collects historical vegetation around this point"""
    sentinel = ee.ImageCollection("COPERNICUS/S2_SR") 
    sentinel = sentinel.map(addNDVI)

    total_geometry = google_points.geometry()
    sentinel_filtered = sentinel.filterDate(start_date, end_date).filterBounds(total_geometry)

    def custom_reducer(image):
        def image_properties(feature):
            extra_info = ee.Feature(None, {
                'imgID': image.id(),
                'date': image.date().format("YYYY-MM-dd HH:mm:ss")
                }).copyProperties(feature)
            return extra_info

        sentinel_mean = image.reduceRegions(
            collection= google_points,
            reducer= ee.Reducer.mean(),
            scale= scale
         ).map(image_properties)
         
        return sentinel_mean

    intermediate = sentinel_filtered.map(custom_reducer).flatten()
    return geemap.ee_to_geopandas(intermediate)