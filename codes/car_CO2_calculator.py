import geopandas as gpd
import pandas as pd
import os, sys

def calculateCarCO2emissions(src_file, output_dir):
    # Read data into GeoDataFrame
    data = gpd.read_file(src_file)

    print(data.head())
