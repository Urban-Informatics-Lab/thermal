import os
import ee
import pandas as pd
from ee.geometry import Geometry

import logging
logger = logging.getLogger(__name__)

from datetime import date

def run(ids:list[str], google_points: Geometry, start_date: date, end_date: date, scale:int = 100, **kwargs) -> pd.DataFrame:
    """Collects land surface temperature"""
    lst_raw = ee.ImageCollection('MODIS/006/MOD11A1')
    lst = lst_raw.select('LST_Day_1km', 'LST_Night_1km').filterDate(start_date, end_date)

    lst_info = lst.getRegion(google_points, scale).getInfo()
    lst_df = pd.DataFrame(lst_info)
    lst_df.columns=lst_df.iloc[0]
    lst_df = lst_df[1:]
    lst_df['datetime'] = pd.to_datetime(lst_df['time'], unit='ms')

    # while lst doesn't seem to suffer from this, we want to try and get daily stats by agg over the date
    lst_df_daymean = lst_df.groupby(['longitude','latitude',lst_df['datetime'].dt.date]).mean().drop(columns=['datetime','time','id']).reset_index()
    lst_day = lst_df_daymean.groupby(['longitude','latitude'])['LST_Day_1km'].apply(list).tolist()
    lst_night = lst_df_daymean.groupby(['longitude','latitude'])['LST_Night_1km'].apply(list).tolist()

    lst_data = pd.DataFrame({
        'id': ids,
        'lst_day': lst_day,
        'lst_night': lst_night
    })

    return lst_data