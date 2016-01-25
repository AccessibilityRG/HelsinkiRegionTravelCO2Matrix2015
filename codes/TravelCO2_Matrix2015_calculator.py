"""
   Copyright (C) 2016  Accessibility Research Group (Tenkanen).
   Developer: Henrikki Tenkanen, University of Helsinki, Finland.

   This script parses Helsinki Region Travel CO2 Matrix 2015 and pushes it to PostGIS Table.
   A specific Java application called RouteCarbonCalculator (programmed by Jaani Lahtinen, modified by Henrikki Tenkanen),
   and specific Python functionalities (found in funclib.py) are used to create the CO2 matrix.

   Multiprocessing is enabled: You can initialize multiple processes and run them simultaneously.

   NOTICE: Before using the tools you need to adjust the Database connection details in base.py

   Process includes following steps:

   1. Calculate the CO2 emissions with RouteCarbonCalculator2015.jar for PT (update CO2 emissions to Java application beforehand if needed)
   2. Calculate CO2 emissions for Private Car
   3. Move Carbon files to a new dedicated location on a disk
   4. Combine PT and Car results
   5. Push Carbon files to PostGIS

   --------------
   License:
   --------------
   TravelCO2_Matrix2015_calculator.py by Accessibility Research Group (University of Helsinki) is licensed under a Creative Commons Attribution 4.0 International License.
   More information about license: http://creativecommons.org/licenses/by/4.0/

   """

import os, sys
import funclib
from base import DATA_TABLE
import multiprocessing

class co2MatrixCreator ():

    def __init__(self, fl, threadID, start_index, end_index, pt_r_dir, pt_m_dir, car_r_dir, car_m_dir, pt_r_co2_dir, pt_m_co2_dir, car_r_co2_dir, car_m_co2_dir, co2_calculator_path):
        self.fl = fl
        self.threadID = threadID
        self.start_index = start_index
        self.end_index = end_index
        self.pt_r_dir = pt_r_dir
        self.pt_m_dir = pt_m_dir
        self.car_r_dir = car_r_dir
        self.car_m_dir = car_m_dir
        self.pt_r_co2_dir = pt_r_co2_dir
        self.pt_m_co2_dir = pt_m_co2_dir
        self.car_r_co2_dir = car_r_co2_dir
        self.car_m_co2_dir = car_m_co2_dir
        self.co2_calculator_path = co2_calculator_path


def createCO2Matrix(objInstance):
    fl = objInstance.fl
    # ----------------------------
    # Read input file paths
    # ----------------------------
    pt_08_fps = fl.filePathsToList(source_dir=objInstance.pt_r_dir, criteria='Rushhour', fileformat='.txt')
    pt_12_fps = fl.filePathsToList(source_dir=objInstance.pt_m_dir, criteria='Midday', fileformat='.txt')

    car_08_fps = fl.filePathsToList(source_dir=objInstance.car_r_dir, criteria='Ruuhka', fileformat='.shp')
    car_12_fps = fl.filePathsToList(source_dir=objInstance.car_m_dir, criteria='Midday', fileformat='.shp')

    # Start, end indices for rebooting purposes
    start_idx = objInstance.start_index
    end_idx = objInstance.end_index

    # ----------------------------
    # Start processing the files
    # ----------------------------

    # Iterate over Public Transport rushhour files
    for fileidx, ptfp08 in enumerate(pt_08_fps):
        # Skip files if needed
        if fileidx >= start_idx and fileidx < end_idx:
            print("Processing file: %s\nIndex: %s" % (ptfp08, fileidx))

            # Find corresponding pt12 and car files
            ptfp12 = fl.findMatchingFile(source_fp=ptfp08, targetPaths=pt_12_fps)
            carfp08 = fl.findMatchingFile(source_fp=ptfp08, targetPaths=car_08_fps, mode='car')
            carfp12 = fl.findMatchingFile(source_fp=ptfp08, targetPaths=car_12_fps, mode='car')

            # Create File paths
            # -----------------------
            fl.setCO2File(src_file=ptfp08, output_dir=objInstance.pt_r_co2_dir, travel_mode="pt", time='08', threadID=objInstance.threadID)
            fl.setCO2File(src_file=ptfp12, output_dir=objInstance.pt_m_co2_dir, travel_mode="pt", time='12', threadID=objInstance.threadID)
            fl.setCO2File(src_file=carfp08, output_dir=objInstance.car_r_co2_dir, travel_mode="car", time='08', threadID=objInstance.threadID)
            fl.setCO2File(src_file=carfp12, output_dir=objInstance.car_m_co2_dir, travel_mode="car", time='12', threadID=objInstance.threadID)


            # Calculate CO2 emissions for PT using RouteCarbonCalculator (Java application)
            # pt_08_co2file = fl.runRouteCarbonCalculator(src_file=ptfp08, path_to_carbon_calc=objInstance.co2_calculator_path, time='08')
            # pt_12_co2file = fl.runRouteCarbonCalculator(src_file=ptfp12, path_to_carbon_calc=objInstance.co2_calculator_path, time='12')

            # Get File paths
            pt_08_co2file = fl.getCO2File(travel_mode="pt", time='08')
            pt_12_co2file = fl.getCO2File(travel_mode="pt", time='12')

            # Calculate the CO2 results for Car
            #car_08_co2file = fl.calculateCarCO2emissions(src_file=carfp08, time='08')
            #car_12_co2file = fl.calculateCarCO2emissions(src_file=carfp12, time='12')

            # Get File paths
            car_08_co2file = fl.getCO2File(travel_mode="car", time='08')
            car_12_co2file = fl.getCO2File(travel_mode="car", time='12')

            # -----------------------------------------
            # Combine datasets into a single DataFrame
            # -----------------------------------------

            # LIST ORDER MUST MATCH IN FOLLOWING 3 LISTS:
            # Files that will be processed
            fp_list = [pt_08_co2file, pt_12_co2file, car_08_co2file, car_12_co2file]
            # Suffices for the columns in processed files that will be inserted
            name_list = ['_PT_r', '_PT_m', '_Car_r', '_Car_m']
            # Separators for each file
            sep_list = [';', ';', ';', ';']

            # Combine datasets
            co2_emissions = fl.combineDatasets(fp_list=fp_list, sep_list=sep_list, name_list=name_list)

            # ---------------------------------------
            # Parse necessary columns for the Matrix
            # ---------------------------------------
            selected_cols = ['from_id', 'to_id', 'Total CO2_PT_r', 'distanceByPT_PT_r', 'Lines used_PT_r', 'Total CO2_PT_m', 'distanceByPT_PT_m', 'Lines used_PT_m', 'co2FromCar_Car_r', 'distDriven_Car_r', 'co2FromCar_Car_m', 'distDriven_Car_m']
            co2_matrix = co2_emissions[selected_cols]

            # Rename columns
            co2_matrix.columns = ['from_id', 'to_id', 'pt_r_co2', 'pt_r_dd', 'pt_r_l', 'pt_m_co2', 'pt_m_dd', 'pt_m_l', 'car_r_co2', 'car_r_dd', 'car_m_co2', 'car_m_dd']

            # ---------------------------------
            # Create PostGIS table if needed
            # ---------------------------------

            # Create DB engine
            engine = fl.create_DB_engine()

            # Create Table if it does not exist
            #fl.createTableIfNotExist()

            # ---------------------------------
            # Push CO2 data to PostGIS
            # ---------------------------------

            print("Pushing data to table: %s" % DATA_TABLE)
            co2_matrix.to_sql(DATA_TABLE, engine, if_exists='append', index=False)



if __name__ == '__main__':

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

    # =========================================================
    # Initialize function library
    # =========================================================

    fl = funclib.matrixMethods(pt_r_dir=pt_08_dir, pt_m_dir=pt_12_dir, pt_r_co2_dir=pt_08_co2_dir, pt_m_co2_dir=pt_12_co2_dir,
                car_r_dir=car_08_dir, car_m_dir=car_12_dir, car_r_co2_dir=car_08_co2_dir, car_m_co2_dir=car_12_co2_dir,
                co2_calculator_path=co2_calculator)

    # =============================================================
    # Create Process objects ==> Enable multiprocessing in parallel
    # =============================================================

    # NOTICE!
    # You should take care that there is sufficiently memory (RAM) in your computer.
    # Creating too many processes may exceed your memory limit and produce a memory error.
    # 3 processes is the maximum that can be used without problems with computer that has 16GB of RAM.

    # Process1
    # ========

    # Set up start-end indices
    start_idx = 0
    end_idx = 97

    o1 = co2MatrixCreator(fl=fl, threadID="%s_%s", start_index=start_idx, end_index=end_idx,
                          pt_r_dir=pt_08_dir, pt_m_dir=pt_12_dir, pt_r_co2_dir=pt_08_co2_dir, pt_m_co2_dir=pt_12_co2_dir,
                          car_r_dir=car_08_dir, car_m_dir=car_12_dir, car_r_co2_dir=car_08_co2_dir, car_m_co2_dir=car_12_co2_dir,
                          co2_calculator_path=co2_calculator)

    # Process2
    # ========

    # Set up start-end indices
    start_idx = 97
    end_idx = 194

    o2 = co2MatrixCreator(fl=fl, threadID="%s_%s", start_index=start_idx, end_index=end_idx,
                                pt_r_dir=pt_08_dir, pt_m_dir=pt_12_dir, pt_r_co2_dir=pt_08_co2_dir, pt_m_co2_dir=pt_12_co2_dir,
                                car_r_dir=car_08_dir, car_m_dir=car_12_dir, car_r_co2_dir=car_08_co2_dir, car_m_co2_dir=car_12_co2_dir,
                                co2_calculator_path=co2_calculator)
    # Process3
    # ========

    # Set up start-end indices
    start_idx = 194
    end_idx = 293

    o3 = co2MatrixCreator(fl=fl, threadID="%s_%s", start_index=start_idx, end_index=end_idx,
                                pt_r_dir=pt_08_dir, pt_m_dir=pt_12_dir, pt_r_co2_dir=pt_08_co2_dir, pt_m_co2_dir=pt_12_co2_dir,
                                car_r_dir=car_08_dir, car_m_dir=car_12_dir, car_r_co2_dir=car_08_co2_dir, car_m_co2_dir=car_12_co2_dir,
                                co2_calculator_path=co2_calculator)

    # --------------------------------------------------------
    # Run the processes in parallel using multiprocessing.Pool
    # --------------------------------------------------------
    objList = [o1, o2, o3]

    # Create a pool
    pool = multiprocessing.Pool()

    # Run processes in parallel
    pool.map(createCO2Matrix, objList)


