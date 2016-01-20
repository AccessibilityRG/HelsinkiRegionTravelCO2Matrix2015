__author__ = 'hentenka'
import os, sys
import subprocess
import pandas as pd
from base import POSTGIS_DB_NAME, POSTGIS_PORT, POSTGIS_PWD, POSTGIS_USERNAME, IP_ADDRESS, DATA_TABLE
import psycopg2
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import create_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def filePathsToList(source_dir, criteria, fileformat):
    flist = []
    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if criteria in filename and filename.endswith(fileformat):
                flist.append(os.path.join(root, filename))
    return flist

def createMatrixFolder(to_id, outDir):
    dirname = "%sxxx" % str(to_id)[:4]
    fullpath = os.path.join(outDir, dirname)
    if not os.path.isdir(fullpath):
        os.makedirs(fullpath)
    return fullpath

def findMatchingFile(source_fp, targetPaths, mode='pt'):
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

def runRouteCarbonCalculator(src_file, path_to_carbon_calc, output_dir, threadID):
    # Create separate folders for RESULTS and ERRORS
    co2_result_target_dir = os.path.join(output_dir, "RESULTS")
    co2_error_target_dir = os.path.join(output_dir, "ERRORS")

    if not os.path.exists(co2_result_target_dir):
        os.makedirs(co2_result_target_dir)
    if not os.path.exists(co2_error_target_dir):
        os.makedirs(co2_error_target_dir)

    # Create output paths for result, error and ttFile files
    result_file = "%s_CO2.txt" % os.path.basename(src_file).split('.')[0]
    error_file = "%s_CO2_ERRORS.txt" % os.path.basename(src_file).split('.')[0]
    ttFile = "ttFile_%s.txt" % threadID

    # Target paths
    co2_result = os.path.join(co2_result_target_dir, result_file)
    co2_error = os.path.join(co2_error_target_dir, error_file)

    # Parse command
    command = "java -jar %s %s %s %s %s" % (path_to_carbon_calc, src_file, co2_result, co2_error, ttFile)
    print(command)
    subprocess.call(command)

    # Return result path
    return co2_result

def combineDatasets(fp_list, sep_list, name_list):
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

def connect_to_DB():
    # PostGIS Authentication crecedentials
    db_name, host, port, username, pwd = POSTGIS_DB_NAME, IP_ADDRESS, POSTGIS_PORT, POSTGIS_USERNAME, POSTGIS_PWD
    conn_string = "host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, db_name, username, pwd, port)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return conn, cursor

def create_DB_engine():
    # PostGIS Authentication crecedentials
    db_name, host, port, username, pwd = POSTGIS_DB_NAME, IP_ADDRESS, POSTGIS_PORT, POSTGIS_USERNAME, POSTGIS_PWD
    db_url = r'postgresql://%s:%s@%s:%s/%s' % (username, pwd, host, port, db_name)
    engine = create_engine(db_url)
    # Set schema
    Base.metadata.create_all(engine)
    return engine

def createCO2table15(conn, cursor, table_name):
    # Create a table [table_name]
    cursor.execute("CREATE TABLE %s (from_id integer, to_id integer, pt_r_co2 integer, pt_r_dd integer, pt_r_l integer, pt_m_co2 integer, pt_m_dd integer, pt_m_l integer, car_r_co2 integer, car_r_dd integer, car_m_co2 integer, car_m_dd integer);" % table_name)
    conn.commit()

def checkIfDbTableExists(conn, cursor, table):
    cursor.execute("select exists(select relname from pg_class where relname='" + table + "')")
    if cursor.fetchone()[0]:
        print("Table exists already, passing..")
        return True
    print("Creating DB table: %s" % table)
    return False

def createPrimaryKey(col_name):
    # Create connection to DB ==> TODO: This should be in class constructor
    conn, cursor = connect_to_DB()
    # Create a primary key to database
    sql = "ALTER TABLE %s ADD COLUMN %s SERIAL" % (DATA_TABLE, col_name)
    print(sql)
    cursor.execute(sql)
    conn.commit()

def vacuumTable(conn, cursor, table):
    # This function only vacuums space for re-use within same table
    # (if required use FULL parameter to entirely free space to the disk
    # (notice: requires a lot of space to do this because a copy is made during the vacuum process))
    old_isolation_level = conn.isolation_level
    conn.set_isolation_level(0)
    sql = "VACUUM (VERBOSE, ANALYZE) %s;" % table
    cursor.execute(sql)
    conn.commit()
    conn.set_isolation_level(old_isolation_level)

def createIndex(conn, cursor, table, column, index_col):
    sql = "CREATE INDEX %s ON %s (%s);" % (index_col, table, column)
    print(sql)

    cursor.execute(sql)
    conn.commit()

def createMatrixIndexes():
    # Create connection to DB
    conn, cursor = connect_to_DB()
    # Create Index for 'to_id' and 'from_id'
    sql = "CREATE INDEX fromididx ON %s (from_id)" % DATA_TABLE
    cursor.execute(sql)
    conn.commit()
    sql = "CREATE INDEX toididx ON %s (to_id)" % DATA_TABLE
    cursor.execute(sql)
    conn.commit()

def setPrimaryKeyCol(conn, cursor, table, key_column):
    sql = "ALTER TABLE %s ADD PRIMARY KEY (%s);" % (table, key_column)
    print(sql)
    cursor.execute(sql)
    conn.commit()

def renameColumns(conn, cursor, table, oldName_newName_dict):
    for old_name, new_name in oldName_newName_dict.items():
        print(old_name, "==>", new_name)
        sql = "ALTER TABLE %s RENAME COLUMN %s TO %s;" % (table, old_name, new_name)
        cursor.execute(sql)

    conn.commit()



