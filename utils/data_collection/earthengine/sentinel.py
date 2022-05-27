import ee
import pandas as pd
import geemap
import json
from geemap.datasets import merge_dict

from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

from datetime import date

def addNDVI(image):
    return image.addBands(image.normalizedDifference(['B8', 'B4']).rename('NDVI'))

def run(google_points: FeatureCollection, start_date: date, end_date: date, scale:int = 100, **kwargs) -> dict:
    """Collects historical vegetation around this point"""
    sentinel = ee.ImageCollection("COPERNICUS/S2_SR") 
    sentinel = sentinel.map(addNDVI)

    total_geometry = google_points.geometry()
    sentinel_filtered = sentinel\
            .filterDate(start_date, end_date)\
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))\
            .filterBounds(total_geometry)

    def custom_reducer(image):
        def image_properties(feature):
            injecting = ee.Feature(None, {
                'imgID': image.id(),
                'date': image.date().format("YYYY-MM-dd HH:mm:ss")
                })
            return feature.setGeometry(None).copyProperties(injecting)

        sentinel_mean = image.reduceRegions(
            collection= google_points,
            reducer= ee.Reducer.mean(),
            scale= scale
         ).map(image_properties)
         
        return sentinel_mean

    return {
        "selectors":[
            "date",
            "B1",
            "B2",
            "B3",
            "B4",
            "B5",
            "B6",
            "B7",
            "B8",
            "B8A",
            "B9",
            "B11",
            "B12",
            "AOT",
            "WVP"
            ],
        "collection":sentinel_filtered.map(custom_reducer).flatten()
    }
    # logger.debug('Raw Features: {}'.format(json.dumps(intermediate.getInfo(), indent=4, sort_keys=True)))
    # logger.info('Sentinel Feature Properties: {}'.format(intermediate.first().propertyNames().getInfo()))
    # geop = geemap.ee_to_geopandas(intermediate)
    # logger.info(geop)
    # logger.info("GEOP Columns: {}".format(geop.columns))
    # return intermediate