import os
from tracemalloc import start
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
    rtma_collection = ee.ImageCollection("NOAA/NWS/RTMA")
    total_geometry = google_points.geometry()
    rtma = rtma_collection.filterDate(start_date, end_date).filterBounds(total_geometry)

    ee_start_date = ee.Date(start_date)
    ee_end_date = ee.Date(end_date)

    # going to get a little bit tricky here, want to compress the amount of data we need to use
    n_months = ee.Number(ee_end_date.difference(ee_start_date,'month')).floor()
    months_sequence = ee.List.sequence(0, n_months)

    def monthly_compression(n_month):
        month_start = ee_start_date.advance(n_month, 'month')
        month_end = month_start.advance(1, 'month')
        rtma_monthly_filtered = rtma.filterDate(month_start, month_end)
        rtma_monthly_float = rtma_monthly_filtered.map(lambda x: x.toFloat())
        rtma_monthly = rtma_monthly_float.mean()
        return rtma_monthly.set('system:time_start', month_start.millis())

    rtma_monthly = ee.ImageCollection(months_sequence.map(monthly_compression))

    # this could 100% be improved
    rtma_monthly = rtma_monthly.filter(ee.Filter.listContains('system:band_names', 'TMP'))

    def custom_reducer(image):
        def image_properties(feature):
            extra_info = ee.Feature(None, {
                'imgID': image.id(),
                'date': image.date().format("YYYY-MM-dd HH:mm:ss")
                }).copyProperties(feature)
            return extra_info

        rtma_regional_mean = image.reduceRegions(
            collection= google_points,
            reducer= ee.Reducer.mean(),
            scale= scale
        ).map(image_properties)
         
        return rtma_regional_mean

    return {
        "selectors":[
            "date",
            "HGT",
            "PRES",
            "TMP",
            "DPT",
            "UGRD",
            "VGRD",
            "SPFH",
            "WDIR",
            "WIND",
            "GUST",
            "VIS",
            "TCDC",
            "ACPC01"
        ],
        "collection": rtma_monthly.map(custom_reducer).flatten()
    }