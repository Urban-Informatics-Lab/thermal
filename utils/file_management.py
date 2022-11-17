import os
import json
import geemap
import ee
import geopandas as gpd
import pandas as pd
import logging
import yaml

from typing import Tuple

from utils.data_collection.footprint_area import footprint_id

logger = logging.getLogger(__name__)

# class customEccoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, np.integer):
#             return int(obj)
#         if isinstance(obj, np.floating):
#             return float(obj)
#         if isinstance(obj, np.ndarray):
#             return obj.tolist()
#         return super(customEccoder, self).default(obj)


def initialize(
    base_dir: str,
    data_dir: str,
    city: str = None,
    settings: str = None,
    commandline_settings: dict = {},
) -> Tuple[dict, str]:
    """Load global settings and the city specific settings"""
    city_path = generate_structure(data_dir=data_dir, city=city)

    default_settings_file = os.path.join(base_dir, 'default_settings.yml')
    default_settings = {}

    if os.path.exists(default_settings_file):
        with open(default_settings_file, 'r') as file:
            default_settings = {**default_settings, **yaml.safe_load(file)}
            logger.info("Default Settings: {}".format(default_settings))
    else:
        logger.info("Default settings not loaded...")

    settings_file = settings
    logger.info("Custom Settings Path: {}".format(settings_file))
    custom_settings = {}

    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            custom_settings = {**custom_settings, **yaml.safe_load(file)}
            logger.info("Custom Settings: {}".format(custom_settings))
    else:
        logger.info("Custom settings not loaded...")

    config = {**default_settings, **custom_settings, **commandline_settings}
    return config, city_path


def generate_structure(data_dir: str, city: str = None) -> str:
    """Returns the city_path which will be used in later computations"""
    if city is not None:
        # what we want most of the time
        city_path = os.path.join(data_dir, city)
    else:
        if os.path.exists(data_dir):
            contents_dir = [d for d in os.listdir(
                data_dir) if os.path.isdir(os.path.join(data_dir, d))]
            contents_intdir = list(
                filter(lambda x: x.isnumeric(), contents_dir))
            contents_int = [int(x) for x in contents_intdir]

            if len(contents_int) > 0:
                city_path = os.path.join(data_dir, str(max(contents_int)+1))
            else:
                city_path = os.path.join(data_dir, '1')
        else:
            city_path = os.path.join(data_dir, '1')

    os.makedirs(city_path, exist_ok=True)
    return city_path


def get_footprints(city_path: str, epsg: str = None) -> str:
    """Check if the building footprints have been provided"""
    footprints_path = os.path.join(city_path, 'footprints.geojson')
    if not os.path.exists(footprints_path):
        raise ImportError('Cannot find footprints file to define buildings')

    footprints = gpd.read_file(footprints_path)
    logger.info("Finding footprints: {}".format(footprints.columns))

    if 'id' not in footprints.columns:
        footprints = footprint_id(footprints)
        footprints.to_file(footprints_path, driver='GeoJSON')

    if epsg is not None:
        footprints = footprints.to_crs(epsg=epsg)

    return footprints


def save_data(processed_classes: dict, city_path: str, export: bool = False, custom_selectors: list = [], **kwargs):
    logger.info('Saving...')
    collected_datadir = os.path.join(city_path, 'satellite')
    os.makedirs(collected_datadir, exist_ok=True)
    for key, value in processed_classes.items():
        collection = value['collection']
        selectors = custom_selectors + value['selectors']
        if export:
            # we want this if we're running a larger computation which is going to kill resources
            logger.info(f"Exporting {key} Data to Drive...")
            task = ee.batch.Export.table.toDrive(
                description=key,
                folder=collected_datadir,
                fileFormat="CSV",
                selectors=selectors,
                collection=collection
            )
            task.start()
        else:
            logger.info("Saving Data Locally...")
            data_path = os.path.join(collected_datadir, key+'.csv')
            geodf = pd.DataFrame(geemap.ee_to_geopandas(collection))
            retaining_df = geodf.loc[:, selectors]
            retaining_df.to_csv(data_path)
            logger.info("Sample of {} data:\n{}".format(
                key, retaining_df.head(5)))
