import os, sys
import subprocess
import psycopg2
import funclib as fl

"""This script parses Helsinki Region Travel CO2 Matrix 2015 using a
   Java application called RouteCarbonCalculator (programmed by Jaani Lahtinen)

   Process includes following steps:

   1. Calculate the CO2 emissions with RouteCarbonCalculator for PT
   2. Calculate CO2 emissions for Private Car
   3. Combine PT and Car results
   4. Move Carbon files to a new dedicated location on a disk
   5. Push Carbon files to PostGIS
   6. Pull Carbon emission matrix from PostGIS and create a text-file based CO2 Matrix

   """
# -------------
# Folder paths
# -------------

pt_08_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_PT_klo08_FixedKalkati\Joukkoliikenne"
pt_12_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_PT_klo12_FixedKalkati\Joukkoliikenne"

car_08_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_Autoilu_Ruuhka"
car_12_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_Autoilu_Midday"


# Read files from the paths
pt_08_fps = fl.filePathsToList(source_dir=pt_08_dir, criteria='Rushhour', fileformat='.txt')
pt_12_fps = fl.filePathsToList(source_dir=pt_12_dir, criteria='Midday', fileformat='.txt')

car_08_fps = fl.filePathsToList(source_dir=car_08_dir, criteria='Ruuhka', fileformat='.shp')
car_12_fps = fl.filePathsToList(source_dir=car_12_dir, criteria='Midday', fileformat='.shp')




