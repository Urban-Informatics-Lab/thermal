from concurrent.futures import process
import ee
from datetime import date
from geopandas import GeoDataFrame

from typing import Union

import logging
logger = logging.getLogger(__name__)

from utils.data_collection.footprint_area import to_featurecollection
from utils.data_collection.earthengine.dateutil import datelist

# the kinds of data we're going to work with
from utils.data_collection.earthengine import cmip, lst_terra, lst_aqua, sar, sentinel_1C, sentinel_2A, elevation, era5, era5_land, noaa, landsat8, viirs, dynamicworld

def manage(
    footprints: GeoDataFrame,
    **config):
    '''Runs all of the specific satellite commands'''
    ee.Initialize() # may want to hook this up later to config file
    feature_collection = to_featurecollection(footprints, **config)

    # each of these data sources should have a common 'run' function with a common interface
    data_classes = [
        cmip,
        dynamicworld,
        # era5_land
        # lst_terra,
        # lst_aqua,
        # ecostress,
        # elevation,
        # era5,
        # noaa,
        # sar,
        # sentinel_2A,
        # sentinel_1C,
        # viirs,
        landsat8
    ]
    
    processed_classes = {}
    for data_class in data_classes:
        classname = data_class.__name__.split('.')[-1]

        logger.info("Processing Dataclass: {}".format(classname))
        processed_classes[classname] = data_class.run(
            feature_collection, 
            **config
        )

    return processed_classes