from concurrent.futures import process
import ee
from datetime import date
from geopandas import GeoDataFrame

from typing import Union

import logging
logger = logging.getLogger(__name__)

from utils.data_collection.footprint_area import points_googleformat, footprint_id
from utils.data_collection.earthengine.dateutil import datelist
from utils.data_collection.earthengine import lst

def manage(footprints: GeoDataFrame, epsg: Union[int, str], start_date: date, end_date: date, **config):
    '''Runs all of the specific satellite commands'''
    ee.Initialize() # may want to hook this up later to config file

    if 'id' not in footprints.columns:
        footprints['id'] = footprint_id(footprints)

    points_list = points_googleformat(footprints, epsg=epsg)
    google_points = ee.Geometry.MultiPoint(points_list)

    # each of these data sources should have a common 'run' function with a common interface
    data_classes = [
        lst
    ]

    # first collect all the data into a dictionary full of information
    # maybe ideal format:
    # data_type:
    #   footprint_id:
    #       data:pd.DataFrame
    #           datetime
    #           value
    
    processed_classes = {}

    for data_class in data_classes:
        classname = data_class.__name__.split('.')[-1]
        processed_classes[classname] = data_class.run(
            footprints['id'],
            google_points, 
            start_date=start_date, 
            end_date=end_date, 
            **config
        )

    return processed_classes

