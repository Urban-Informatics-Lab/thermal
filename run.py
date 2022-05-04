from ast import Str
from email.policy import default
import os
import sys
import argparse
import typing
from typing import Union
import yaml
import logging

from utils.file_management import get_footprints, initialize, save_data
from utils.data_collection.earthengine.manage import manage

def create_datadir(data_path:str):
    os.makedirs(data_path, exist_ok=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--data_dir', type=str, default='data')
    parser.add_argument('--city', type=str, default=None)
    parser.add_argument('--settings', type=str, default='settings.yml')
    parser.add_argument('--projection_epsg', type=str, default='EPSG:3857') # pseudo-mercator, which is in meters but not perfect for distance calculations
    parser.add_argument('--default_epsg', type=str, default='EPSG:4326')
    parser.add_argument('--export_vector', type=bool, default=False)
    parser.add_argument(
        "--log-level",
        default=logging.INFO,
        type=lambda x: getattr(logging, x),
        help="Configure the logging level."
    )

    args = parser.parse_args()
    logging.basicConfig(
        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
        level=args.log_level
    )

    logger = logging.getLogger(__name__)

    config:dict = vars(args)
    logger.info("Command Line Configuration: {}".format(config))

    base_dir:str = os.path.dirname(os.path.realpath(__file__))
    config, city_path = initialize(
        base_dir=base_dir,
        data_dir=args.data_dir,
        city=args.city,
        settings=args.settings,
        commandline_settings=config
    )

    logger.info("Full Configuration File: {}".format(config))

    # now into the management code - first want to get the building footprints and the regional statistics
    footprints = get_footprints(city_path=city_path)
    results = manage(footprints[:4], **config)
    logger.info('Saving files....')
    save_data(results, city_path=city_path, **config)
    logger.info('Saved!')


    



