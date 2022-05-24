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
    weather_images = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY")
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
            "dewpoint_temperature_2m",
            "temperature_2m",
            "skin_temperature",
            "soil_temperature_level_1",
            "soil_temperature_level_2",
            "soil_temperature_level_3",
            "soil_temperature_level_4",
            "lake_bottom_temperature",
            "lake_ice_depth",
            "lake_ice_temperature",
            "lake_mix_layer_depth",
            "lake_mix_layer_temperature",
            "lake_shape_factor",
            "lake_total_layer_temperature",
            "snow_albedo",
            "snow_cover",
            "snow_density",
            "snow_depth",
            "snow_depth_water_equivalent",
            "snowfall",
            "snowmelt",
            "temperature_of_snow_layer",
            "temperature_of_snow_layer",
            "volumetric_soil_water_layer_1",
            "volumetric_soil_water_layer_2",
            "volumetric_soil_water_layer_3",
            "volumetric_soil_water_layer_4",
            "forecast_albedo",
            "surface_latent_heat_flux",
            "surface_net_solar_radiation",
            "surface_net_thermal_radiation",
            "surface_sensible_heat_flux",
            "surface_solar_radiation_downwards",
            "surface_thermal_radiation_downwards",
            "evaporation_from_bare_soil",
            "evaporation_from_open_water_surfaces_excluding_oceans",
            "evaporation_from_the_top_of_canopy",
            "evaporation_from_the_top_of_canopy",
            "potential_evaporation",
            "runoff",
            "snow_evaporation",
            "sub_surface_runoff",
            "surface_runoff",
            "total_evaporation",
            "u_component_of_wind_10m",
            "v_component_of_wind_10m",
            "surface_pressure",
            "total_precipitation",
            "leaf_area_index_high_vegetation",
            "leaf_area_index_low_vegetation"
        ],
        "collection":weather.map(custom_reducer).flatten()
    }