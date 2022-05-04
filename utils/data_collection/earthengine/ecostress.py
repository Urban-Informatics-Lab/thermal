import os
import ee
import pandas as pd
import geemap
from ee import FeatureCollection


def run(google_points: FeatureCollection, start_date: date, end_date: date, scale:int = 100, **kwargs) -> FeatureCollection:
    """Collects historical vegetation around this point"""
    sentinel = ee.ImageCollection("NASA/GRACE/MASS_GRIDS/LAND")

    total_geometry = google_points.geometry()
    sentinel_filtered = sentinel.filterDate(start_date, end_date).filterBounds(total_geometry)

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

    return sentinel_filtered.map(custom_reducer).flatten()