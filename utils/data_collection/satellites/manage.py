import ee

from utils.data_collection.satellites.thermal import run

def manage(compute_area: list, epsg: int):
    '''Runs all of the specific satellite commands'''
    ee.Initialize() # may want to hook this up later to config file
    ee_geometry = ee.Geometry.Polygon(compute_area, proj=epsg)
    
