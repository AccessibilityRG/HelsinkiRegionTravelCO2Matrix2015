import pandas as pd
import geopandas as gpd
import numpy as np
import os, sys
import funclib
from base import DATA_TABLE
import multiprocessing

"""This script creates Helsinki Region Travel CO2 Matrix 2015 text-file version.
   Data is pulled from PostGIS table that was created using TravelCO2_Matrix2015_calculator.py script.

   Multiprocessing is enabled: You can initialize multiple threads and run them simultaneously.

   NOTICE: Before using the tools you need to adjust the Database connection details in base.py

   Process includes following steps:

   1. Create in PostGIS primary_key and indices for 'from_id' and 'to_id' columns
   2.Iterate over YKR grid IDs one by one
   3. Pull data from PostGIS table which 'to_id' corresponds to specified YKR_ID
   4. Select data (i.e. 'from_id's) that matches with YKR grid IDs
       ==> There were extra cells calculated around Helsinki Region to decrease border error)
   5. Write the data into a text-file (e.g. 'travel_co2_to_5789456.txt')

   """

class co2TextMatrixCreator ():

    def __init__(self, fl, threadID, start_index, end_index, ykr_grid_df, output_co2_dir):
        self.fl = fl
        self.threadID = threadID
        self.start_index = start_index
        self.end_index = end_index
        self.ykr_grid_df = ykr_grid_df
        self.output_co2_dir = output_co2_dir


def createCO2TextMatrix(obj):

    # Determine parameters
    fl = obj.fl
    ykr_grid = obj.ykr_grid_df
    output_co2_dir = obj.output_co2_dir
    start_index = obj.start_index
    end_index = obj.end_index

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
                        'car_r_co2', 'car_r_dd', 'car_r_fc',
                        'car_m_t', 'car_m_d', 'car_m_fc']
            data = data[datacols]

            # Create folder if does not exist
            targetDir = fl.createMatrixFolder(output_co2_dir, to_id)
            # Create filename
            outname = "travel_co2_to_ %s.txt" % to_id
            # Outputpath
            outfile = os.path.join(targetDir, outname)
            # Write results to disk
            data.to_csv(outfile, sep=';', index=False, mode='w', float_format="%.0f")

if __name__ == '__main__':

    # -------------
    # File paths
    # -------------

    ykr_fp = r"C:\HY-Data\HENTENKA\Python\MassaAjoNiputus\ShapeFileet\MetropAccess_YKR_grid\MetropAccess_YKR_grid_EurefFIN.shp"
    #ykr_fp = r"C:\HY-Data\HENTENKA\Opetus\2015_GIS_Prosessiautomatisointi\MetropAccess_YKR_grid\MetropAccess_YKR_grid_EurefFIN.shp"
    outDir = r"E:\Matriisiajot2015\RESULTS\HelsinkiRegion_TravelCO2Matrix2015"

    # --------------
    # Read YKR_grid
    # --------------
    ykr = gpd.read_file(ykr_fp)
    # Initialize matrix methods
    fl = funclib.matrixMethods(matrix_dir=outDir, ykr_grid=ykr)

    # =========================================================
    # Do PostGIS stuff first
    # =========================================================

    # Connect to DB
    fl.connect_to_DB()

    # Add columns for fuel consumption
    dtype = 'REAL'

    col_name = 'car_r_fc'
    #fl.addColumnToTable(table=DATA_TABLE, column_name=col_name, data_type=dtype)

    col_name = 'car_m_fc'
    #fl.addColumnToTable(table=DATA_TABLE, column_name=col_name, data_type=dtype)

    # Create Primary key
    #fl.createPrimaryKey(col_name='Id')
    # Set Primary key
    #fl.setPrimaryKeyCol(table=DATA_TABLE, key_column='Id')

    # Calculate the Fuel consumption
    # -------------------------------
    # Fuel consumption is approximately 7.3 l / 100 km (taking into account diesel/petrol + different car age groups)

    # Calculate fuel consumption factor
    ages = ['y', 'm', 'o']
    sizes = ['S', 'M', 'L']
    formula = 'mean'
    fuels = ['p', 'd']
    PD = funclib.fuelConsumption(fuels=fuels, ages=ages, sizes=sizes, formula=formula)

    # Get the result
    fuel_consumption = np.round(PD.result, 1)  # ==> 7.3 l per 100 km

    # Calculate the fuel consumption into DB
    input_col = 'car_r_dd'
    target_col = 'car_r_fc'
    #fl.calculateFuelConsumptionDB(input_col=input_col, target_col=target_col, fuel_consumption_factor=fuel_consumption)

    input_col = 'car_m_dd'
    target_col = 'car_m_fc'
    #fl.calculateFuelConsumptionDB(input_col=input_col, target_col=target_col, fuel_consumption_factor=fuel_consumption)


    # Create PostGIS Indices for 'to_id' and 'from_id' to enable fast lookups
    fl.createMatrixIndexes()

    sys.exit()
    # ==============================================================
    # Create process objects ==> Enable multiprocessing in parallel
    # ==============================================================

    # NOTICE!
    # You should take care that there is sufficiently memory (RAM) in your computer.
    # Creating too many processes may exceed your memory limit and produce a memory error.
    # At least 5 processes can be used without problems with computer that has 16GB of RAM.

    # Process1
    # =======
    # Set up start-end indices
    start_idx = 0
    end_idx = 50
    o1 = co2TextMatrixCreator(fl=fl, threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_df=ykr, output_co2_dir=outDir)

    # Process2
    # =======
    # Set up start-end indices
    start_idx = 50
    end_idx = 100
    o2 = co2TextMatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_df=ykr, output_co2_dir=outDir)

    # Process3
    # =======
    # Set up start-end indices
    start_idx = 150
    end_idx = 200
    o3 = co2TextMatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_df=ykr, output_co2_dir=outDir)

    # Process4
    # =======
    # Set up start-end indices
    start_idx = 200
    end_idx = 250
    o4 = co2TextMatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_df=ykr, output_co2_dir=outDir)

    # Process5
    # =======
    # Set up start-end indices
    start_idx = 250
    end_idx = 293
    o5 = co2TextMatrixCreator(threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_df=ykr, output_co2_dir=outDir)

    # --------------------------------------------------------
    # Run the processes in parallel using multiprocessing.Pool
    # --------------------------------------------------------
    objList = [o1, o2, o3, o4, o5]

    # Create a pool
    pool = multiprocessing.Pool()

    # Run processes in parallel
    pool.map(createCO2TextMatrix, objList)
