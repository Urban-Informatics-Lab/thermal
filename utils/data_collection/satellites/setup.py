import ee
import os


def setup(**kwargs):
    """Sets up the earth engine for queries and runs the stuff"""
    ee.Initialize()
    return