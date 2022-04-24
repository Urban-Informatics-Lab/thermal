import os
import sys
import geopandas as gpd
from geopandas import GeoDataFrame

from typing import Union
from shapely.geometry import Polygon, Point
from shapely.geometry import MultiPoint

import logging
logger = logging.getLogger(__name__)

def convex_hull(footprints: gpd.GeoDataFrame, buffer_dist:int = 1e3) -> Polygon:
    """returns a list containing the bottom left and the top right 
    points in the sequence
    Here, we use min and max four times over the collection of points
    """
    mpt = MultiPoint(footprints.geometry.centroid)
    convex_hull = mpt.convex_hull.buffer(buffer_dist) # buffer out the convex hull by buffer_dist in meters
    if convex_hull.area / 1e6 > 10e3:
        logger.error("Total region requested is greater than a city.")
        raise ValueError
    return convex_hull

def prep_googleformat(compute_area: Polygon) -> list:
    '''Preps the shapely file into a list of lists we can use with earth engine'''
    x, y = compute_area.exterior.coords.xy
    return [ list(i) for i in zip(x,y) ]

def points_googleformat(footprints: GeoDataFrame, epsg:Union[int,str]) -> list:
    '''Preps the building list into centroid points which will be used to query the stats'''
    if type(epsg) == int:
        epsg = 'EPSG:{}'.format(epsg)

    footprint_centroids = footprints.geometry.to_crs(epsg).centroid
    return [ [geom.xy[0][0], geom.xy[1][0]] for geom in footprint_centroids ]

def footprint_id(footprints: GeoDataFrame) -> list[int]:
    geo_strings = footprints.geometry.map(str)
    return geo_strings.map(lambda x: hash(x) % ((sys.maxsize + 1) * 2))
