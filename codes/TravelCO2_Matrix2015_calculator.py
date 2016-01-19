import os, sys
import psycopg2
import funclib as fl
import car_CO2_calculator as cco2

"""This script parses Helsinki Region Travel CO2 Matrix 2015 using a
   Java application called RouteCarbonCalculator (programmed by Jaani Lahtinen, modified by Henrikki Tenkanen)

   Process includes following steps:

   1. Calculate the CO2 emissions with RouteCarbonCalculator2015.jar for PT (update CO2 emissions to Java application beforehand if needed)
   2. Calculate CO2 emissions for Private Car
   3. Move Carbon files to a new dedicated location on a disk
   4. Combine PT and Car results
   5. Push Carbon files to PostGIS
   7. Pull Carbon emission matrix from PostGIS and create a text-file based CO2 Matrix

   """
# -------------
# Folder paths
# -------------

# Public Transport & Car source file folder paths
pt_08_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_PT_klo08_FixedKalkati\Joukkoliikenne"
pt_12_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_PT_klo12_FixedKalkati\Joukkoliikenne"
car_08_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_Car_Rushhour"
car_12_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_Car_Midday"

# CO2 output paths for PT and car
pt_08_co2_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_PT_klo08_CARBON"
pt_12_co2_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_PT_klo12_CARBON"
car_08_co2_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_Car_Rushhour_CARBON"
car_12_co2_dir = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_Car_Midday_CARBON"

# Final output path for "Helsinki Region Travel CO2 Matrix 2015"
co2_matrix_2015 = r"E:\Matriisiajot2015\RESULTS\HelsinkiRegion_TravelCO2Matrix2015"

# Path to RouteCarbonCalculator
co2_calculator = r"C:\HY-Data\HENTENKA\KOODIT\HelsinkiRegionTravelCO2\codes\CarbonCalculator\RouteCarbonCalculator2015.jar"

# ----------------------------
# Read input file paths
# ----------------------------

pt_08_fps = fl.filePathsToList(source_dir=pt_08_dir, criteria='Rushhour', fileformat='.txt')
pt_12_fps = fl.filePathsToList(source_dir=pt_12_dir, criteria='Midday', fileformat='.txt')

car_08_fps = fl.filePathsToList(source_dir=car_08_dir, criteria='Ruuhka', fileformat='.shp')
car_12_fps = fl.filePathsToList(source_dir=car_12_dir, criteria='Midday', fileformat='.shp')

# Start, end indices for rebooting purposes
start_idx = 0
end_idx = 1 #293

# ----------------------------
# Start processing the files
# ----------------------------

# Iterate over Public Transport rushhour files
for fileidx, ptfp08 in enumerate(pt_08_fps):
    # Skip files if needed
    if fileidx >= start_idx and fileidx < end_idx:

        # Find corresponding pt12 and car files
        ptfp12 = fl.findMatchingFile(source_fp=ptfp08, targetPaths=pt_12_fps)
        carfp08 = fl.findMatchingFile(source_fp=ptfp08, targetPaths=car_08_fps, mode='car')
        carfp12 = fl.findMatchingFile(source_fp=ptfp08, targetPaths=car_12_fps, mode='car')

        # Calculate CO2 emissions for PT using RouteCarbonCalculator (Java application)
        pt_08_co2file = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_PT_klo08_CARBON\RESULTS\100_Massa-ajo_2015_Joukkoliikenne_Rushhour_CO2.txt" #       pt_08_co2file = fl.runRouteCarbonCalculator(src_file=ptfp08, path_to_carbon_calc=co2_calculator, output_dir=pt_08_co2_dir)

        # Calculate the CO2 results for Car
        car_08_co2file = r"E:\Matriisiajot2015\RESULTS\MassaAjot2015_Car_Rushhour_CARBON\CarTT_Ruuhka_100_Car_Matrix2015_CO2_emissions.txt" #car_08_co2file = cco2.calculateCarCO2emissions(src_file=carfp08, output_dir=car_08_co2_dir)

        # Combine datasets into a single DataFrame
        # -----------------------------------------

        # LIST ORDER MUST MATCH IN FOLLOWING 3 LISTS:
        # Files that will be processed
        fp_list = [pt_08_co2file, car_08_co2file]
        # Suffices for the columns in processed files that will be inserted
        name_list = ['_PT_r', '_Car_r']
        # Separators for each file
        sep_list = [';', ';']

        # Combine datsets
        co2_emissions = fl.combineDatasets(fp_list=fp_list, sep_list=sep_list, name_list=name_list)

        print(co2_emissions.head())
        print(co2_emissions.columns)

        # ---------------------------------------
        # Parse necessary columns for the Matrix
        # ---------------------------------------
        selected_cols = ['from_id', 'to_id', 'Total CO2_PT_r', 'co2FromCar_Car_r']

        # ---------------------------------
        # Create PostGIS table if needed
        # ---------------------------------













