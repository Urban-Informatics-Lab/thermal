from datetime import date
import os
import ee
import pandas as pd
import geemap
from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

def addNDVI(image):
    return image.addBands(image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI'))

def run(google_points: FeatureCollection, start_date: date, end_date: date, scale: int = 100, **kwargs) -> dict:
    """Collects land surface temperature"""
    lst_raw = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")

    total_geometry = google_points.geometry()
    lst = lst_raw.filterDate(start_date, end_date).filterBounds(total_geometry)
    lst = lst.map(addNDVI)

    def custom_reducer(image):
        # scored = ee.Algorithms.Landsat.simpleCloudScore(image)
        # mask = scored.select(['cloud']).lte(20)
        # image = image.updateMask(mask)

        def image_properties(feature):
            injecting = ee.Feature(None, {
                'imgID': image.id(),
                'date': image.date().format("YYYY-MM-dd HH:mm:ss")
            })
            return feature.copyProperties(injecting)

        # now trying to map this into a filtering scheme
        qaMask = image.select('QA_PIXEL').bitwiseAnd(31).eq(0)
        saturationMask = image.select('QA_RADSAT').eq(0)

        lst_masked = image.updateMask(qaMask).updateMask(saturationMask)
        lst_reduced = lst_masked.reduceRegions(
            collection=google_points,
            reducer=ee.Reducer.mean(),
            scale=scale
        ).map(image_properties)

        return lst_reduced

    return {
        "selectors": [
            "date",
            "ST_B10",  # this is the land surface temperature
            "ST_QA",
            "ST_ATRAN",
            "ST_CDIST",
            "ST_DRAD",
            "ST_EMIS",
            "ST_EMSD",
            "ST_TRAD",
            "ST_URAD",
            "SR_B1",
            "SR_B2",
            "SR_B3",
            "SR_B4",
            "SR_B5",
            "SR_B6",
            "SR_B7",
            "NDVI"
        ],
        "collection": lst.map(custom_reducer).flatten()
    }
    # return lst.map(custom_reducer).flatten()
