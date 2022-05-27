import os
import sys
import geopandas as gpd
from geopandas import GeoDataFrame
import ee
import numpy as np
import uuid

from typing import Union
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.geometry import MultiPoint

import geemap

import logging
logger = logging.getLogger(__name__)


def convex_hull(footprints: gpd.GeoDataFrame, buffer_dist: int = 1e3) -> Polygon:
    """returns a list containing the bottom left and the top right 
    points in the sequence
    Here, we use min and max four times over the collection of points
    """
    mpt = MultiPoint(footprints.geometry.centroid)
    # buffer out the convex hull by buffer_dist in meters
    convex_hull = mpt.convex_hull.buffer(buffer_dist)
    if convex_hull.area / 1e6 > 10e3:
        logger.error("Total region requested is greater than a city.")
        raise ValueError
    return convex_hull


def ee_polygon(geometry: Polygon) -> ee.Geometry.Polygon:
    '''Preps the shapely file into a list of lists we can use with earth engine'''
    x, y = geometry.exterior.coords.xy
    cords = np.dstack((x, y)).tolist()
    return ee.Geometry.Polygon(cords)


def ee_multipolygon(geometry: MultiPolygon) -> ee.Geometry.Polygon:
    '''Preps the shapely file into a list of lists we can use with earth engine'''
    x, y = geometry.geoms[0].exterior.coords.xy  # this may be a fuck up
    cords = np.dstack((x, y)).tolist()
    return ee.Geometry.Polygon(cords[0])


def ee_point(geometry: Point) -> ee.Geometry.Point:
    x, y = geometry.xyexperiements
# def to_featurecollection(footprints: GeoDataFrame, buffer_size: int = 20, **kwargs) -> ee.FeatureCollection:
#     '''Preps the building list into centroid points which will be used to query the stats'''
#     logger.info("Buffering {} meters...".format(buffer_size))
#     features = []
#     for index in range(len(footprints)):
#         geometry = footprints.iloc[index].geometry
#         if type(geometry) == Point:
#             ee_geom = ee_point(geometry)
#         elif type(geometry) == Polygon:
#             ee_geom = ee_polygon(geometry)
#         elif type(geometry) == MultiPolygon:
#             ee_geom = ee_multipolygon(geometry)
#         else:
#             raise TypeError('Footprint geometry not supported.')

#         data = footprints.loc[index, ~footprints.columns.isin(['geometry'])]
#         features.append(ee.Feature(ee_geom.buffer(buffer_size), dict(data)))

#     return ee.FeatureCollection(features)


def to_featurecollection(footprints: GeoDataFrame, buffer_size: int = 100, **kwargs) -> ee.FeatureCollection:
    return geemap.geopandas_to_ee(footprints).map(lambda x: x.buffer(buffer_size))


def footprint_id(footprints: GeoDataFrame) -> list[int]:
    """Provides an id for each footprint based on the """
    footprints['id'] = [str(uuid.uuid5(uuid.NAMESPACE_DNS, str(x)))[-5:]
                        for x in footprints.geometry]
    return footprints
