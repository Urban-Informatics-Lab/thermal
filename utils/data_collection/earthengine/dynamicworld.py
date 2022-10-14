from datetime import date
import os
import ee
import pandas as pd
import geemap
from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

def run(google_points: FeatureCollection, start_date: date, end_date: date, scale: int = 100, **kwargs) -> dict:
    """Collects land surface temperature"""
    dw_raw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
    total_geometry = google_points.geometry()
    dw = dw_raw.filterDate(start_date, end_date).filterBounds(total_geometry)

    def custom_reducer(image):
        def image_properties(feature):
            injecting = ee.Feature(None, {
                'imgID': image.id(),
                'date': image.date().format("YYYY-MM-dd HH:mm:ss")
            })
            return feature.copyProperties(injecting)

        dw_reduced = image.reduceRegions(
            collection=google_points,
            reducer=ee.Reducer.mean(),
            scale=scale
        ).map(image_properties)

        return dw_reduced

    return {
        "selectors": [
            "date",
            "water",
            "trees",
            "grass",
            "flooded_vegetation",
            "crops",
            "shrub_and_scrub",
            "built",
            "bare",
            "snow_and_ice",
            "label"
        ],
        "collection": dw.map(custom_reducer).flatten()
    }
    # return lst.map(custom_reducer).flatten()
