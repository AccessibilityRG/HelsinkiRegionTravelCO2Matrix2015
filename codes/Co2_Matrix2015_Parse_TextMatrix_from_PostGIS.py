import pandas as pd
import geopandas as gpd
import os, sys
import funclib as fl
from base import DATA_TABLE
import threading

"""This script creates Helsinki Region Travel CO2 Matrix 2015 text-file version.
   Data is pulled from PostGIS table that was created using TravelCO2_Matrix2015_calculator.py script.

   Multiprocessing is enabled: You can initialize multiple threads and run them simultaneously.

   Process includes following steps:

   1. Create in PostGIS primary_key and indices for 'from_id' and 'to_id' columns
   2.Iterate over YKR grid IDs one by one
   3. Pull data from PostGIS table which 'to_id' corresponds to specified YKR_ID
   4. Select data (i.e. 'from_id's) that matches with YKR grid IDs
       ==> There were extra cells calculated around Helsinki Region to decrease border error)
   5. Write the data into a text-file (e.g. 'travel_co2_to_5789456.txt')

   """

class co2TextMatrixCreator (threading.Thread):

    def __init__(self, threadID, start_index, end_index, ykr_grid_df, output_co2_dir):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.start_index = start_index
        self.end_index = end_index
        self.ykr_grid_df = ykr_grid_df
        self.output_co2_dir = output_co2_dir

    def run(self):
        print("Starting thread: %s" % self.threadID)
        createCO2TextMatrix(ykr_grid=self.ykr_grid_df, output_co2_dir=self.output_co2_dir,
                            start_index=self.start_index, end_index=self.end_index)
        print("All done in thread: %s" % self.threadID)


def createCO2TextMatrix(ykr_grid, output_co2_dir, start_index, end_index):

    # Iterate over individual YKR_IDs and create
    for index, row in ykr_grid.iterrows():
        if index >= start_index and index < end_index:
            # Get to_id
            to_id = row['YKR_ID']
            print("Processing ID: %s" % to_id)

            # Connect to Database
            conn, cursor = fl.connect_to_DB()

            # Get unique 'to_id' values from the db
            sql = """SELECT * FROM %s
                       WHERE to_id = %s;""" % (DATA_TABLE, to_id)

            # Read data into DataFrame
            data = pd.read_sql_query(sql, conn)

            # Join ('outer') with YKR_ID to find out missing values and sort the values
            data = ykr[['YKR_ID']].merge(data, left_on='YKR_ID', right_on='from_id', how='outer')

            # Drop dublicate values
            data = data.drop_duplicates(subset='YKR_ID')

            # Set 'YKR_ID' value for 'from_id'
            data['from_id'] = data['YKR_ID']

            # Fill NaN values with -1
            data = data.fillna(value=-1)

            # Select output data
            datacols = ['from_id', 'to_id',
                        'pt_r_co2', 'pt_r_dd', 'pt_r_l',
                        'pt_m_co2', 'pt_m_dd', 'pt_m_l',
                        'car_r_co2', 'car_r_dd',
                        'car_m_t', 'car_m_d']
            data = data[datacols]

            # Create folder if does not exist
            targetDir = fl.createMatrixFolder(output_co2_dir, to_id)
            # Create filename
            outname = "travel_co2_to_ %s.txt" % to_id
            # Outputpath
            outfile = os.path.join(targetDir, outname)
            # Write results to disk
            data.to_csv(outfile, sep=';', index=False, mode='w', float_format="%.0f")

    
# -------------
# File paths
# -------------

ykr_fp = r"C:\HY-Data\HENTENKA\Python\MassaAjoNiputus\ShapeFileet\MetropAccess_YKR_grid\MetropAccess_YKR_grid_EurefFIN.shp"
outDir = r"E:\Matriisiajot2015\RESULTS\HelsinkiRegion_TravelCO2Matrix2015"

# =========================================================
# Do PostGIS stuff first
# =========================================================

# Create Primary key
fl.createPrimaryKey(col_name='Id')

# Create PostGIS Indices for 'to_id' and 'from_id' to enable fast lookups
fl.createMatrixIndexes()

# --------------
# Read YKR_grid
# --------------
ykr = gpd.read_file(ykr_fp)

# =========================================================
# Create threads ==> Enable multiprocessing in parallel
# =========================================================

# NOTICE!
# You should take care that there is sufficiently memory (RAM) in your computer.
# Creating too many threads may exceed your memory limit and produce a memory error.
# At least 5 threads can be used without problems with computer that has 16GB of RAM.

# THREAD1
# =======
# Set up start-end indices
start_idx = 0
end_idx = 50
thread1 = co2TextMatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_df=ykr, output_co2_dir=outDir)

# THREAD2
# =======
# Set up start-end indices
start_idx = 50
end_idx = 100
thread2 = co2TextMatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_df=ykr, output_co2_dir=outDir)

# THREAD3
# =======
# Set up start-end indices
start_idx = 150
end_idx = 200
thread3 = co2TextMatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_df=ykr, output_co2_dir=outDir)

# THREAD4
# =======
# Set up start-end indices
start_idx = 200
end_idx = 250
thread4 = co2TextMatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_df=ykr, output_co2_dir=outDir)

# THREAD5
# =======
# Set up start-end indices
start_idx = 250
end_idx = 293
thread5 = co2TextMatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_df=ykr, output_co2_dir=outDir)

# ----------------
# Run the threads
# ----------------
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()