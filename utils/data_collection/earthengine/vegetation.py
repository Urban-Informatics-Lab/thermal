import os
import ee
import pandas as pd
from ee.geometry import Geometry

import logging
logger = logging.getLogger(__name__)

from datetime import date

def addNDVI(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

def run(ids:list[str], google_points: Geometry, start_date: date, end_date: date, scale:int = 100, **kwargs) -> pd.DataFrame:
    """Collects land surface temperature"""
    s2 = ee.ImageCollection("COPERNICUS/S2_SR")
    s2_date = s2.filterDate(start_date, end_date)
    ndvi = s2_date.map(addNDVI).select('NDVI')

    ndvi_info = ndvi.getRegion(google_points, scale).getInfo()
    ndvi_df = pd.DataFrame(ndvi_info)
    ndvi_df.columns=ndvi_df.iloc[0]
    ndvi_df = ndvi_df[1:]
    ndvi_df['datetime'] = pd.to_datetime(ndvi_df['time'], unit='ms')

    # while lst doesn't seem to suffer from this, we want to try and get daily stats by agg over the date
    ndvi_df_daymean = ndvi_df.groupby(['longitude','latitude',ndvi_df['datetime'].dt.date]).mean().drop(columns=['datetime','time']).reset_index()
    ndvi_terms = ndvi_df_daymean.groupby(['longitude','latitude'])['NDVI'].apply(list).tolist()
    ndvi_return = pd.DataFrame({
        'id': ids,
        'lst_day': ndvi_terms
    })

    return ndvi_return