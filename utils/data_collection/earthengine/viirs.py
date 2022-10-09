from datetime import date
import ee
from ee import FeatureCollection

import logging
logger = logging.getLogger(__name__)

def run(google_points: FeatureCollection, start_date: date, end_date: date, scale: int = 100, **kwargs) -> dict:
    """Collects VIIRS Data"""
    viirs_raw = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")

    total_geometry = google_points.geometry()
    viirs = viirs_raw.filterDate(start_date, end_date).filterBounds(total_geometry)

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

        viirs_reduced = image.reduceRegions(
            collection=google_points,
            reducer=ee.Reducer.mean(),
            scale=scale
        ).map(image_properties)

        return viirs_reduced

    return {
        "selectors": [
            "date",
            "avg_rad",
            "cf_cvg"
        ],
        "collection": viirs.map(custom_reducer).flatten()
    }