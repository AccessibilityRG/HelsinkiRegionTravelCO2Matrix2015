import pandas as pd
import geopandas as gpd
import numpy as np
import os, sys
import funclib
from base import DATA_TABLE
import multiprocessing

"""
   Copyright (C) 2016  Accessibility Research Group (Tenkanen).
   Developer: Henrikki Tenkanen, University of Helsinki, Finland.

   This script creates Helsinki Region Travel CO2 Matrix 2015 text-file version.
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

   --------------
   License:
   --------------
   CO2_Matrix2015_Parse_TextMatrix_from_PostGIS.py by Accessibility Research Group (University of Helsinki) is licensed under a Creative Commons Attribution 4.0 International License.
   More information about license: http://creativecommons.org/licenses/by/4.0/

   """

class co2TextMatrixCreator ():

    def __init__(self, fl="", threadID="", start_index="", end_index="", ykr_grid_df="", ykr_grid_fp="", output_co2_dir=""):
        self.fl = fl
        self.threadID = threadID
        self.start_index = start_index
        self.end_index = end_index
        self.ykr_grid_df = ykr_grid_df
        self.ykr_grid_fp = ykr_grid_fp
        self.output_co2_dir = output_co2_dir


def createCO2TextMatrix(obj):

    # Determine parameters
    fl = obj.fl
    fl.create_DB_engine()
    ykr_grid = gpd.read_file(obj.ykr_grid_fp)
    output_co2_dir = obj.output_co2_dir
    start_index = obj.start_index
    end_index = obj.end_index

    print("Start iterating")

    # Iterate over individual YKR_IDs and create
    for index, row in ykr_grid.iterrows():
        if index >= start_index and index < end_index:
            # Get to_id
            to_id = row['YKR_ID']
            print("Index: %s,Processing ID: %s" % (index, to_id))

            # Get unique 'to_id' values from the db
            data = fl.pullDataFromDB(to_id)

            # Join ('outer') with YKR_ID to find out missing values and sort the values
            data = ykr_grid[['YKR_ID']].merge(data, left_on='YKR_ID', right_on='from_id', how='outer')

            # Drop dublicate values
            data = data.drop_duplicates(subset='YKR_ID')

            # Set 'YKR_ID' value for 'from_id'
            data['from_id'] = data['YKR_ID']

            # Drop rows with NaN in from_id
            data = data.ix[~data['from_id'].isnull()]

            # Ensure that 'to_id' is present in all cases
            data['to_id'] = to_id

            # Fill NaN values with -1
            data = data.fillna(value=-1)

            # Select output data
            datacols = ['from_id', 'to_id',
                        'pt_r_co2', 'pt_r_dd', 'pt_r_l',
                        'pt_m_co2', 'pt_m_dd', 'pt_m_l',
                        'car_r_co2', 'car_r_dd', 'car_r_fc',
                        'car_m_co2', 'car_m_dd', 'car_m_fc']
            data = data[datacols]

            # Set data type to int for other columns than fuel consumption
            intcols = datacols[0:10] + datacols[11:13]
            data[intcols] = data[intcols].astype(int)

            # Convert float numbers to 2-decimal strings
            data = data.apply(fl.floatToStr, axis=1, column='car_r_fc')
            data = data.apply(fl.floatToStr, axis=1, column='car_m_fc')

            # Change -1.0 to -1
            data = data.replace({'-1.0': '-1'})

            # Create folder if does not exist
            targetDir = fl.createMatrixFolder(outDir=output_co2_dir, to_id=to_id)
            # Create filename
            outname = "travel_co2_to_%s.txt" % to_id
            # Outputpath
            outfile = os.path.join(targetDir, outname)
            #print("Saving results to: %s\n" % outfile)
            # Write results to disk
            data.to_csv(outfile, sep=';', index=False, mode='w', float_format="%.0f")

if __name__ == '__main__':

    # -------------
    # File paths
    # -------------

    ykr_fp = r"C:\HY-Data\HENTENKA\Python\MassaAjoNiputus\ShapeFileet\MetropAccess_YKR_grid\MetropAccess_YKR_grid_EurefFIN.shp"
    #ykr_fp = r"C:\HY-Data\HENTENKA\Opetus\2015_GIS_Prosessiautomatisointi\MetropAccess_YKR_grid\MetropAccess_YKR_grid_EurefFIN.shp"
    outDir = r"E:\Matriisiajot2015\RESULTS\HelsinkiRegion_TravelCO2Matrix2015"

    # Initialize matrix methods
    fl = funclib.matrixMethods(matrix_dir=outDir, ykr_grid_fp=ykr_fp)

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
    #PD = funclib.fuelConsumption(fuels=fuels, ages=ages, sizes=sizes, formula=formula)

    # Get the result
    #fuel_consumption = np.round(PD.result, 1)  # ==> 7.3 l per 100 km

    # Calculate the fuel consumption into DB
    input_col = 'car_r_dd'
    target_col = 'car_r_fc'
    #fl.calculateFuelConsumptionDB(input_col=input_col, target_col=target_col, fuel_consumption_factor=fuel_consumption)

    input_col = 'car_m_dd'
    target_col = 'car_m_fc'
    #fl.calculateFuelConsumptionDB(input_col=input_col, target_col=target_col, fuel_consumption_factor=fuel_consumption)


    # Create PostGIS Indices for 'to_id' and 'from_id' to enable fast lookups
    #fl.createMatrixIndexes()


    # ==============================================================
    # Create process objects ==> Enable multiprocessing in parallel
    # ==============================================================

    # NOTICE!
    # You should take care that there is sufficiently memory (RAM) in your computer.
    # Creating too many processes may exceed your memory limit and produce a memory error.
    # At least 3 processes can be used without problems with computer that has 16GB of RAM.

    # Process1
    # =======
    # Set up start-end indices
    start_idx = 0
    end_idx = 2205
    o1 = co2TextMatrixCreator(fl=fl, threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_fp=ykr_fp, output_co2_dir=outDir)

    # Process2
    # =======
    # Set up start-end indices
    start_idx = 2205
    end_idx = 4410
    o2 = co2TextMatrixCreator(fl=fl, threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_fp=ykr_fp, output_co2_dir=outDir)

    # Process3
    # =======
    # Set up start-end indices
    start_idx = 4410
    end_idx = 6615
    o3 = co2TextMatrixCreator(fl=fl, threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_fp=ykr_fp, output_co2_dir=outDir)

    # Process4
    # =======
    # Set up start-end indices
    start_idx = 6615
    end_idx = 8820
    o4 = co2TextMatrixCreator(fl=fl, threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_fp=ykr_fp, output_co2_dir=outDir)

    # Process5
    # =======
    # Set up start-end indices
    start_idx = 8820
    end_idx = 11025
    o5 = co2TextMatrixCreator(fl=fl, threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_fp=ykr_fp, output_co2_dir=outDir)

    # Process6
    # =======
    # Set up start-end indices
    start_idx = 11025
    end_idx = 13232
    o6 = co2TextMatrixCreator(fl=fl, threadID="%s_%s" % (start_idx, end_idx), start_index=start_idx, end_index=end_idx, ykr_grid_fp=ykr_fp, output_co2_dir=outDir)

    # --------------------------------------------------------
    # Run the processes in parallel using multiprocessing.Pool
    # --------------------------------------------------------
    objList = [o1, o2, o3]
    #objList = [o4, o5, o6]

    print("%s parallel processes created." % len(objList))

    pool = multiprocessing.Pool()

    # Run processes in parallel
    pool.map(createCO2TextMatrix, objList)
