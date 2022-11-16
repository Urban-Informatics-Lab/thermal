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
    cimp_raw = ee.ImageCollection('NASA/NEX-DCP30_ENSEMBLE_STATS')
    total_geometry = google_points.geometry()
    cimp = cimp_raw\
        .filterDate(start_date, end_date)\
        .filter(ee.Filter.eq('scenario', 'rcp60'))\
        .filterBounds(total_geometry)

    def custom_reducer(image):
        def image_properties(feature):
            injecting = ee.Feature(None, {
                'imgID': image.id(),
                'date': image.date().format("YYYY-MM-dd HH:mm:ss")
            })
            return feature.copyProperties(injecting)

        cimp_reduced = image.reduceRegions(
            collection=google_points,
            reducer=ee.Reducer.mean(),
            scale=scale
        ).map(image_properties)

        return cimp_reduced

    return {
        "selectors": [
            "date",
            "pr_mean",
            "pr_quartile25",
            "pr_median",
            "pr_quartile75",
            "tasmin_mean",
            "tasmin_quartile25",
            "tasmin_median",
            "tasmin_quartile75",
            "tasmax_mean",
            "tasmax_quartile25",
            "tasmax_median",
            "tasmax_quartile75",
        ],
        "collection": cimp.map(custom_reducer).flatten()
    }
    # return lst.map(custom_reducer).flatten()
