import os
import ee
import pandas as pd
import geemap

from ee import FeatureCollection
from ee.geometry import Geometry

import logging
logger = logging.getLogger(__name__)

from datetime import date

def run(google_points: FeatureCollection, start_date: date, end_date: date, scale:int = 100, **kwargs) -> dict:
    """Collects land surface temperature"""
    weather_images = ee.ImageCollection("ECMWF/ERA5/MONTHLY")
    total_geometry = google_points.geometry()
    weather = weather_images.filterDate(start_date, end_date).filterBounds(total_geometry)

    def custom_reducer(image):
        def image_properties(feature):
            extra_info = ee.Feature(None, {
                'imgID': image.id(),
                'date': image.date().format("YYYY-MM-dd HH:mm:ss")
                }).copyProperties(feature)
            return extra_info

        weather_mean = image.reduceRegions(
            collection= google_points,
            reducer= ee.Reducer.mean(),
            scale= scale
         ).map(image_properties)
         
        return weather_mean

    return {
        "selectors":[
            "date",
            "mean_2m_air_temperature",
            "minimum_2m_air_temperature",
            "maximum_2m_air_temperature",
            "dewpoint_2m_temperature",
            "total_precipitation",
            "surface_pressure",
            "mean_sea_level_pressure",
            "u_component_of_wind_10m",
            "v_component_of_wind_10m"
        ],
        "collection":weather.map(custom_reducer).flatten()
    }