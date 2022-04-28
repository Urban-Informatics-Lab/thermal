from concurrent.futures import process
import ee
from datetime import date
from geopandas import GeoDataFrame

from typing import Union

import logging
logger = logging.getLogger(__name__)

from utils.data_collection.footprint_area import points_googleformat, footprint_id
from utils.data_collection.earthengine.dateutil import datelist

# the kinds of data we're going to work with
from utils.data_collection.earthengine import lst, vegetation, elevation, weather

def manage(
    footprints: GeoDataFrame,
    projection_epsg: Union[int, str], 
    default_epsg: Union[int, str], 
    start_date: date, 
    end_date: date, 
    **config):
    '''Runs all of the specific satellite commands'''
    ee.Initialize() # may want to hook this up later to config file

    if type(projection_epsg) == int:
        logger.info('Parsing EPSG to string...')
        epsg = 'EPSG:{}'.format(epsg)

    if 'id' not in footprints.columns:
        logger.info('Generating footprint ids...')
        footprints.loc[:,'id'] = footprint_id(footprints, projection_epsg)

    points_list = points_googleformat(footprints, projection_epsg, default_epsg)
    google_points = ee.FeatureCollection([ee.Geometry.Point(point) for point in points_list])

    # each of these data sources should have a common 'run' function with a common interface
    data_classes = [
        lst,
        elevation,
        # weather,
        vegetation
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

        logger.info("Processing Dataclass: {}".format(classname))
        processed_classes[classname] = data_class.run(
            footprints['id'],
            google_points, 
            start_date=start_date, 
            end_date=end_date, 
            **config
        )

    return processed_classes