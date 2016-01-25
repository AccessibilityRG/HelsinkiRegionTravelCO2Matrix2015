"""
   Copyright (C) 2016  Accessibility Research Group (Tenkanen).
   Developer: Henrikki Tenkanen, University of Helsinki, Finland.

   These classes are used to create the Helsinki Region Travel CO2 Matrix 2015 text-file version.

   Functionalities are controlled and used from two files:
    - TravelCO2_Matrix2015_calculator.py
    - Co2_Matrix2015_Parse_TextMatrix_from_PostGIS

   --------------
   License:
   --------------
   CO2_Matrix2015_Parse_TextMatrix_from_PostGIS.py by Accessibility Research Group (University of Helsinki) is licensed under a Creative Commons Attribution 4.0 International License.
   More information about license: http://creativecommons.org/licenses/by/4.0/

   """

import os, sys
import subprocess
import numpy as np
import pandas as pd
import geopandas as gpd
from base import POSTGIS_DB_NAME, POSTGIS_PORT, POSTGIS_PWD, POSTGIS_USERNAME, IP_ADDRESS, DATA_TABLE
import psycopg2
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import create_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class matrixMethods ():

    def __init__(self, pt_r_dir="", pt_m_dir="", car_r_dir="", car_m_dir="", pt_r_co2_dir="", pt_m_co2_dir="", car_r_co2_dir="", car_m_co2_dir="", co2_calculator_path="", matrix_dir="", ykr_grid="", ykr_grid_fp=""):
        # File paths
        self.pt_r_dir = pt_r_dir
        self.pt_m_dir = pt_m_dir
        self.car_r_dir = car_r_dir
        self.car_m_dir = car_m_dir
        self.pt_r_co2_dir = pt_r_co2_dir
        self.pt_m_co2_dir = pt_m_co2_dir
        self.car_r_co2_dir = car_r_co2_dir
        self.car_m_co2_dir = car_m_co2_dir
        self.co2_calculator_path = co2_calculator_path
        self.matrix_dir = matrix_dir
        self.ykr_grid = ykr_grid
        self.ykr_grid_fp = ykr_grid_fp

        # Database connection
        self.conn = None
        self.cursor = None
        self.db_name = POSTGIS_DB_NAME
        self.host = IP_ADDRESS
        self.port = POSTGIS_PORT
        self.username = POSTGIS_USERNAME
        self.pwd = POSTGIS_PWD
        self.engine = None

        # Result files
        self.pt_08_co2file = None
        self.pt_08_errorFile = None
        self.pt_08_ttFile = None

        self.pt_12_co2file = None
        self.pt_12_errorFile = None
        self.pt_12_ttFile = None

        self.car_08_co2file = None
        self.car_12_co2file = None



    # =============
    # GETTERS
    # =============

    def getConn(self):
        return self.conn
    def getCursor(self):
        return self.cursor
    def getCO2File(self, travel_mode, time):
        if travel_mode.lower() == 'pt':
            if time.lower() in ['08', 'r', '8', 'rushhour']:
                return self.pt_08_co2file
            return self.pt_12_co2file
        elif travel_mode.lower() == 'car':
            if time.lower() in ['08', 'r', '8', 'rushhour']:
                return self.car_08_co2file
            return self.car_12_co2file
        else:
            return Exception("Travel mode %s or time %s is incorrect!" % (travel_mode, time))

    # =============
    # SETTERS
    # =============

    def setCO2File(self, src_file, output_dir, travel_mode, time, threadID):
        if time.lower() in ['08', 'r', '8', 'rushhour']:
            if travel_mode.lower() == 'pt':
                self.pt_08_co2file, self.pt_08_errorFile, self.pt_08_ttFile = self.parseCO2FilePath(src_file=src_file, output_dir=output_dir, travel_mode=travel_mode, threadID=threadID)
            elif travel_mode.lower() == 'car':
                self.car_08_co2file = self.parseCO2FilePath(src_file=src_file, output_dir=output_dir, travel_mode=travel_mode, threadID=threadID)
            else:
                raise Exception("Travel mode %s or time %s is incorrect!" % (travel_mode, time))
        else:
            if travel_mode.lower() == 'pt':
                self.pt_12_co2file, self.pt_12_errorFile, self.pt_12_ttFile = self.parseCO2FilePath(src_file=src_file, output_dir=output_dir, travel_mode=travel_mode, threadID=threadID)
            elif travel_mode.lower() == 'car':
                self.car_12_co2file = self.parseCO2FilePath(src_file=src_file, output_dir=output_dir, travel_mode=travel_mode, threadID=threadID)
            else:
                raise Exception("Travel mode %s or time %s is incorrect!" % (travel_mode, time))

    # =============
    # METHODS
    # =============

    def parseCO2FilePath(self, src_file, output_dir, travel_mode, threadID):

        if travel_mode.lower() in ['pt']:
            # Create separate folders for RESULTS and ERRORS
            co2_result_target_dir = os.path.join(output_dir, "RESULTS")
            co2_error_target_dir = os.path.join(output_dir, "ERRORS")

            if not os.path.exists(co2_result_target_dir):
                os.makedirs(co2_result_target_dir)
            if not os.path.exists(co2_error_target_dir):
                os.makedirs(co2_error_target_dir)

            # Create output paths for result, error and ttFile files
            error_file = "%s_CO2_ERRORS.txt" % os.path.basename(src_file).split('.')[0]
            ttFile = "ttFile_%s.txt" % threadID

            # Target error path
            co2_error = os.path.join(co2_error_target_dir, error_file)
            # Target CO2 path
            result_file = "%s_CO2.txt" % os.path.basename(src_file).split('.')[0]
        else:
            co2_result_target_dir = output_dir
            # Target CO2 path
            result_file = "%s_CO2_emissions.txt" % os.path.basename(src_file).split('.')[0]

        co2_result = os.path.join(co2_result_target_dir, result_file)

        if travel_mode.lower() == 'pt':
            return co2_result, co2_error, ttFile
        return co2_result

    def filePathsToList(self, source_dir, criteria, fileformat):
        flist = []
        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                if criteria in filename and filename.endswith(fileformat):
                    flist.append(os.path.join(root, filename))
        return flist

    def createMatrixFolder(self, to_id, outDir):
        dirname = "%sxxx" % str(to_id)[:4]
        fullpath = os.path.join(outDir, dirname)
        if not os.path.isdir(fullpath):
            os.makedirs(fullpath)
        return fullpath

    def findMatchingFile(self, source_fp, targetPaths, mode='pt'):
        search_folder = os.path.dirname(targetPaths[0])
        Source_ID = os.path.basename(source_fp).split('_')[0]
        for targetfile in targetPaths:
            if mode == 'car':
                target_ID = os.path.basename(targetfile).split('_')[2]
            else:
                target_ID = os.path.basename(targetfile).split('_')[0]
            if target_ID == Source_ID:
                return targetfile
        print("Error: Could not find corresponding target_file for %s in %s" % (Source_ID, search_folder))
        sys.exit()

    def pullDataFromDB(self, to_id):
        # Get unique 'to_id' values from the db
        sql = """SELECT * FROM %s
                  WHERE to_id = %s;""" % (DATA_TABLE, to_id)
        # Read data into DataFrame
        data = pd.read_sql_query(sql, self.engine)

        return data


    def floatToStr(self, row, column):
        row[column] = str(np.round(row[column], 2))
        return row

    def runRouteCarbonCalculator(self, src_file, path_to_carbon_calc, time):
        if time.lower() in ['08', '8', 'r']:
            # Target paths
            co2_result = self.pt_08_co2file
            co2_error = self.pt_08_errorFile
            ttFile = self.pt_08_ttFile
        else:
            # Target paths
            co2_result = self.pt_12_co2file
            co2_error = self.pt_12_errorFile
            ttFile = self.pt_12_ttFile

        # Parse command
        command = "java -jar %s %s %s %s %s" % (path_to_carbon_calc, src_file, co2_result, co2_error, ttFile)
        print(command)
        subprocess.call(command)

        # Return result path
        return co2_result

    def combineDatasets(self, fp_list, sep_list, name_list):
        # Create an initial DataFrame of the first file
        data = pd.read_csv(fp_list[0], sep_list[0], index_col=False)

        # Rename columns based on value on name_list
        data.columns = [colname+name_list[0] for colname in data.columns]

        # Rename 'from_id' and 'to_id' back to original
        data = data.rename(columns={'from_id'+name_list[0]: 'from_id', 'to_id'+name_list[0]: 'to_id'})

        # Remove the initial file from fp_list and sep_list
        fp_list, sep_list, name_list = fp_list[1:], sep_list[1:], name_list[1:]

        # Merge files one by one
        for index, fp in enumerate(fp_list):
            # Read other file
            other = pd.read_csv(fp, sep=sep_list[index], index_col=False)
            # Rename columns based on value on name_list
            other.columns = [colname+name_list[index] for colname in other.columns]
            # Rename 'RouteID' back to original
            other = other.rename(columns={'from_id'+name_list[index]: 'from_id', 'to_id'+name_list[index]: 'to_id'})
            # Ensure that 'from_id' and 'to_id' are integer type
            other[['from_id', 'to_id']] = other[['from_id', 'to_id']].astype(int)
            # Make a table join
            data = data.merge(other, on=['from_id', 'to_id'])

        # Return DataFrame
        return data

    def connect_to_DB(self):
        # PostGIS Authentication crecedentials
        conn_string = "host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (self.host, self.db_name, self.username, self.pwd, self.port)
        self.conn = psycopg2.connect(conn_string)
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor

    def create_DB_engine(self):
        # PostGIS Authentication crecedentials
        db_url = r'postgresql://%s:%s@%s:%s/%s' % (self.username, self.pwd, self.host, self.port, self.db_name)
        self.engine = create_engine(db_url)
        # Set schema
        Base.metadata.create_all(self.engine)
        return self.engine

    def createTableIfNotExist(self):
        # Create Table if it does not exist
        if not self.checkIfDbTableExists(table=DATA_TABLE):
            self.createCO2table15(table_name=DATA_TABLE)

    def createCO2table15(self, table_name):
        # Create a table [table_name]
        self.cursor.execute("CREATE TABLE %s (from_id integer, to_id integer, pt_r_co2 integer, pt_r_dd integer, pt_r_l integer, pt_m_co2 integer, pt_m_dd integer, pt_m_l integer, car_r_co2 integer, car_r_dd integer, car_m_co2 integer, car_m_dd integer);" % table_name)
        self.conn.commit()

    def checkIfDbTableExists(self, table):
        self.cursor.execute("select exists(select relname from pg_class where relname='" + table + "')")
        if self.cursor.fetchone()[0]:
            print("Table exists already, passing..")
            return True
        print("Creating DB table: %s" % table)
        return False

    def createPrimaryKey(self, col_name):
        # Create a primary key to database
        sql = "ALTER TABLE %s ADD COLUMN %s SERIAL;" % (DATA_TABLE, col_name)
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def vacuumTable(self, table):
        # This function only vacuums space for re-use within same table
        # (if required use FULL parameter to entirely free space to the disk
        # (notice: requires a lot of space to do this because a copy is made during the vacuum process))
        old_isolation_level = self.conn.isolation_level
        self.conn.set_isolation_level(0)
        sql = "VACUUM (VERBOSE, ANALYZE) %s;" % table
        self.cursor.execute(sql)
        self.conn.commit()
        self.conn.set_isolation_level(old_isolation_level)

    def createIndex(self, table, column, index_col):
        sql = "CREATE INDEX %s ON %s (%s);" % (index_col, table, column)
        print(sql)

        self.cursor.execute(sql)
        self.conn.commit()

    def createMatrixIndexes(self):
        # Create Index for 'to_id' and 'from_id'
        sql = "CREATE INDEX fromididx ON %s (from_id)" % DATA_TABLE
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()
        sql = "CREATE INDEX toididx ON %s (to_id)" % DATA_TABLE
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def setPrimaryKeyCol(self, table, key_column):
        sql = "ALTER TABLE %s ADD PRIMARY KEY (%s);" % (table, key_column)
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def renameColumns(self, table, oldName_newName_dict):
        for old_name, new_name in oldName_newName_dict.items():
            print(old_name, "==>", new_name)
            sql = "ALTER TABLE %s RENAME COLUMN %s TO %s;" % (table, old_name, new_name)
            self.cursor.execute(sql)
        self.conn.commit()

    def addColumnToTable(self, table, column_name, data_type):
        """Data type must be passed as string.
        Supported data types can be found from: http://www.postgresql.org/docs/current/static/datatype.html """

        sql = "ALTER TABLE %s ADD COLUMN %s %s;" % (table, column_name, data_type)
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def calculateFuelConsumptionDB(self, input_col, target_col, fuel_consumption_factor):
        input_col = 'car_r_dd'
        target_col = 'car_r_fc'

        # Meters as per 100 km
        meters_in_100km = 100000.0

        sql = "UPDATE %s SET %s = ((%s / %s) * %s);" % (DATA_TABLE, target_col, input_col, meters_in_100km, fuel_consumption_factor)
        self.commitSQL(sql)

    def commitSQL(self, sql):
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()


    """
   This calculator calculates the CO2 emissions from Car in Helsinki Region.
   CO2 emission per kilometer is 171 grams that is used by Helsinki Region Transport (HRT).
   More info here: http://www.hsljalki.fi/fi/menu/info
    """
    def calculateCarCO2emissions(self, src_file, time, car_co2_emission=171):
        # Read data into GeoDataFrame
        print("Reading: %s" % os.path.basename(src_file))
        data = gpd.read_file(src_file)

        # Calculate CO2 distance (in meters) and total CO2 emissions (in grams per kilometer) from car usage
        print("Calculating the driven distance and CO2 emissions")
        data['distDriven'] = data['Pituus_Ajo'] + data['Pituus_P_E']
        data['co2FromCar'] = (data['distDriven'] / 1000.0) * car_co2_emission

        # Select columns
        slct_cols = ['from_id', 'to_id', 'Pituus_TOT', 'distDriven', 'co2FromCar']
        outdata = data[slct_cols]

        # Create output file
        outname = "%s_CO2_emissions.txt" % os.path.basename(src_file).split('.')[0]

        if time in ['08', '8', 'r']:
            outfp = os.path.join(self.car_r_co2_dir, outname)
        else:
            outfp = os.path.join(self.car_m_co2_dir, outname)

        # Save CO2 data to disk
        print("Saving the CO2 emissions to: %s" % outfp)
        outdata.to_csv(outfp, sep=';', index=False)

        # Return the output path
        return outfp

class fuelConsumption:
    """Abbreviations:
            - Fisrt letter
                p ==> Petrol
                d ==> Diesel
            - Second letter:
               S ==> Small car
               M ==> Midsized car
               L ==> Large car
            - Third letter:
               y ==> young car (0-5 years old)
               m ==> middle aged car (5-10 years old)
               o ==> old car (10+ years old)
        """
    def __init__(self, fuels, ages, sizes, formula):
        # Constructor
        self.fuels = fuels
        self.ages = ages
        self.sizes = sizes
        self.formula = formula

        # Fuel consumption values for different types of cars
        self.fuelValues = {
            # Petrol
            # ------
            # Young
            'pSy' : 6.0,
            'pMy' : 8.0,
            'pLy' : 9.6,

            # Middle aged
            'pSm' : 6.5,
            'pMm' : 8.5,
            'pLm' : 10.6,

            # Old
            'pSo' : 6.8,
            'pMo' : 8.5,
            'pLo' : 10.8,

            # Diesel
            # ------
            # Young
            'dSy' : 4.7,
            'dMy' : 5.9,
            'dLy' : 7.4,

            # Middle aged
            'dSm' : 4.9,
            'dMm' : 6.3,
            'dLm' : 7.6,

            # Old
            'dSo' : 5.5,
            'dMo' : 6.2,
            'dLo' : 7.7,
        }

        # Run fuel consumption calculations
        self.result = self.calculateConsumption(sizes=self.sizes, ages=self.ages, fuels=self.fuels, formula=formula)

    # ----------
    # GETTERS
    # ----------

    def getValue(self, fuel='p', age='y', size='S'):
        return self.fuelValues["%s%s%s" % (fuel, size, age)]

    def calculateConsumption(self, sizes, ages, fuels, formula='mean'):
        # Calculates the fuel consumption estimate using all types of cars
        fc_values = []

        # Iterate over parameters and fetch the consumption values
        for fuel in fuels:
            for age in ages:
                for size in sizes:
                    fc_values.append(self.getValue(fuel=fuel, age=age, size=size))

        # Calculate statistics
        if formula == 'mean':
            return np.mean(fc_values)
        elif formula == 'median':
            return np.median(fc_values)






