import os
import ee
import pandas as pd
from ee.geometry import Geometry

import logging
logger = logging.getLogger(__name__)

from datetime import date

def run(ids:list[str], google_points: Geometry, start_date: date, end_date: date, scale:int = 100, **kwargs) -> pd.DataFrame:
    """Collects land surface temperature"""
    era5_raw = ee.ImageCollection("ECMWF/ERA5/DAILY")
    era5 = era5_raw.filterDate(start_date, end_date)

    era5_info = era5.getRegion(google_points, scale).getInfo()
    era_df = pd.DataFrame(era5_info)
    era_df.columns=era_df.iloc[0]
    era_df = era_df[1:]
    era_df['datetime'] = pd.to_datetime(era_df['time'], unit='ms')

    # while lst doesn't seem to suffer from this, we want to try and get daily stats by agg over the date
    mean_2m_air_temperature = era_df.groupby(['longitude','latitude'])['mean_2m_air_temperature'].apply(list).tolist()
    minimum_2m_air_temperature = era_df.groupby(['longitude','latitude'])['minimum_2m_air_temperature'].apply(list).tolist()
    maximum_2m_air_temperature = era_df.groupby(['longitude','latitude'])['maximum_2m_air_temperature'].apply(list).tolist()
    dewpoint_2m_temperature = era_df.groupby(['longitude','latitude'])['dewpoint_2m_temperature'].apply(list).tolist()
    total_precipitation = era_df.groupby(['longitude','latitude'])['total_precipitation'].apply(list).tolist()
    surface_pressure = era_df.groupby(['longitude','latitude'])['surface_pressure'].apply(list).tolist()
    mean_sea_level_pressure = era_df.groupby(['longitude','latitude'])['mean_sea_level_pressure'].apply(list).tolist()
    u_component_of_wind_10m = era_df.groupby(['longitude','latitude'])['u_component_of_wind_10m'].apply(list).tolist()
    v_component_of_wind_10m = era_df.groupby(['longitude','latitude'])['v_component_of_wind_10m'].apply(list).tolist()

    weather_data = pd.DataFrame({
        'id': ids,
        'mean_2m_air_temperature': mean_2m_air_temperature,
        'minimum_2m_air_temperature': minimum_2m_air_temperature,
        'maximum_2m_air_temperature': maximum_2m_air_temperature,
        'dewpoint_2m_temperature': dewpoint_2m_temperature,
        'total_precipitation': total_precipitation,
        'surface_pressure': surface_pressure,
        'mean_sea_level_pressure': mean_sea_level_pressure,
        'u_component_of_wind_10m': u_component_of_wind_10m,
        'v_component_of_wind_10m': v_component_of_wind_10m
    })

    return weather_data