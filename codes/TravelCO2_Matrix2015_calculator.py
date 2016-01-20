import os, sys
import funclib as fl
import car_CO2_calculator as cco2
from base import DATA_TABLE
import threading
import time

"""This script parses Helsinki Region Travel CO2 Matrix 2015 and pushes it to PostGIS Table.
   A specific Java application called RouteCarbonCalculator (programmed by Jaani Lahtinen, modified by Henrikki Tenkanen),
   and specific Python functionalities (found in funclib.py & car_CO2_calculator.py) are used to create the CO2 matrix.

   Multiprocessing is enabled: You can initialize multiple threads and run them simultaneously.

   Process includes following steps:

   1. Calculate the CO2 emissions with RouteCarbonCalculator2015.jar for PT (update CO2 emissions to Java application beforehand if needed)
   2. Calculate CO2 emissions for Private Car
   3. Move Carbon files to a new dedicated location on a disk
   4. Combine PT and Car results
   5. Push Carbon files to PostGIS

   """

class co2MatrixCreator (threading.Thread):

    def __init__(self, threadID, start_index, end_index, pt_r_dir, pt_m_dir, car_r_dir, car_m_dir, pt_r_co2_dir, pt_m_co2_dir, car_r_co2_dir, car_m_co2_dir, co2_calculator_path):
        threading.Thread.__init__(self)
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

    def run(self):
        print("Starting thread: %s" % self.threadID)
        createCO2Matrix(threadID=self.threadID, start_index=self.start_index, end_index=self.end_index, pt_r_dir=self.pt_r_dir, pt_m_dir=self.pt_m_dir, car_r_dir=self.car_r_dir, car_m_dir=self.car_m_dir,
                        pt_r_co2_dir=self.pt_r_co2_dir, pt_m_co2_dir=self.pt_m_co2_dir, car_r_co2_dir=self.car_r_co2_dir, car_m_co2_dir=self.car_m_co2_dir,
                        co2_calculator_path=self.co2_calculator_path)
        print("All done in thread: %s" % self.threadID)

def createCO2Matrix(threadID, start_index, end_index, pt_r_dir, pt_m_dir, car_r_dir, car_m_dir, pt_r_co2_dir, pt_m_co2_dir, car_r_co2_dir, car_m_co2_dir, co2_calculator_path):

    # ----------------------------
    # Read input file paths
    # ----------------------------
    pt_08_fps = fl.filePathsToList(source_dir=pt_r_dir, criteria='Rushhour', fileformat='.txt')
    pt_12_fps = fl.filePathsToList(source_dir=pt_m_dir, criteria='Midday', fileformat='.txt')

    car_08_fps = fl.filePathsToList(source_dir=car_r_dir, criteria='Ruuhka', fileformat='.shp')
    car_12_fps = fl.filePathsToList(source_dir=car_m_dir, criteria='Midday', fileformat='.shp')

    # Start, end indices for rebooting purposes
    start_idx = start_index
    end_idx = end_index

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

            # Calculate CO2 emissions for PT using RouteCarbonCalculator (Java application)
            pt_08_co2file = fl.runRouteCarbonCalculator(src_file=ptfp08, path_to_carbon_calc=co2_calculator_path, output_dir=pt_r_co2_dir, threadID=threadID)
            pt_12_co2file = fl.runRouteCarbonCalculator(src_file=ptfp12, path_to_carbon_calc=co2_calculator_path, output_dir=pt_m_co2_dir, threadID=threadID)

            # Calculate the CO2 results for Car
            car_08_co2file = cco2.calculateCarCO2emissions(src_file=carfp08, output_dir=car_r_co2_dir)
            car_12_co2file = cco2.calculateCarCO2emissions(src_file=carfp12, output_dir=car_m_co2_dir)

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

            # Connect to Database
            conn, cursor = fl.connect_to_DB()

            # Create DB engine
            engine = fl.create_DB_engine()

            # Create Table if it does not exist
            if not fl.checkIfDbTableExists(conn, cursor, table=DATA_TABLE):
                fl.createCO2table15(conn, cursor, table_name=DATA_TABLE)

            # ---------------------------------
            # Push CO2 data to PostGIS
            # ---------------------------------

            print("Pushing data to table: %s" % DATA_TABLE)
            co2_matrix.to_sql(DATA_TABLE, engine, if_exists='append', index=False)

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
# Create threads ==> Enable multiprocessing in parallel
# =========================================================

# NOTICE!
# You should take care that there is sufficiently memory (RAM) in your computer.
# Creating too many threads may exceed your memory limit and produce a memory error.
# 3 threads is the maximum that can be used without problems with computer that has 16GB of RAM.

# THREAD1
# =======

# Set up start-end indices
start_idx = 121
end_idx = 180

thread1 = co2MatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, pt_r_dir=pt_08_dir, pt_m_dir=pt_12_dir, car_r_dir=car_08_dir, car_m_dir=car_12_dir,
                           pt_r_co2_dir=pt_08_co2_dir, pt_m_co2_dir=pt_12_co2_dir, car_r_co2_dir=car_08_co2_dir, car_m_co2_dir=car_12_co2_dir, co2_calculator_path=co2_calculator)

# THREAD2
# =======

# Set up start-end indices
start_idx = 180
end_idx = 220

thread2 = co2MatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, pt_r_dir=pt_08_dir, pt_m_dir=pt_12_dir, car_r_dir=car_08_dir, car_m_dir=car_12_dir,
                           pt_r_co2_dir=pt_08_co2_dir, pt_m_co2_dir=pt_12_co2_dir, car_r_co2_dir=car_08_co2_dir, car_m_co2_dir=car_12_co2_dir, co2_calculator_path=co2_calculator)

# THREAD3
# =======

# Set up start-end indices
start_idx = 220
end_idx = 293

thread3 = co2MatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, pt_r_dir=pt_08_dir, pt_m_dir=pt_12_dir, car_r_dir=car_08_dir, car_m_dir=car_12_dir,
                           pt_r_co2_dir=pt_08_co2_dir, pt_m_co2_dir=pt_12_co2_dir, car_r_co2_dir=car_08_co2_dir, car_m_co2_dir=car_12_co2_dir, co2_calculator_path=co2_calculator)

# ----------------
# Run the threads
# ----------------
thread1.start()
# Wait for a while before starting next one
time.sleep(60)
thread2.start()
# Wait for a while before starting next one
time.sleep(60)
thread3.start()








