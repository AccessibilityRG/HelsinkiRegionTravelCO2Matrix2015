__author__ = 'hentenka'
import os, sys
import subprocess
import shutil

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

def runRouteCarbonCalculator(src_file, path_to_carbon_calc):
    # Parse command
    command = "java -jar %s %s" % (path_to_carbon_calc, src_file)
    print(command)
    subprocess.call(command)

def moveCO2files(src_file, output_dir):
    # Parse file paths
    src_dir = os.path.dirname(src_file)

    # Parse the names of the source files
    co2_result_name = "%s.RESULT.csv" % os.path.basename(src_file).split('.')[0]
    co2_error_name = "%s.ERRORS.csv" % os.path.basename(src_file).split('.')[0]

    # Parse the full paths
    co2_result = os.path.join(src_dir, co2_result_name)
    co2_error = os.path.join(src_dir, co2_error_name)

    # Create separate folders for RESULTS and ERRORS
    co2_result_target_dir = os.path.join(output_dir, "RESULTS")
    co2_error_target_dir = os.path.join(output_dir, "ERRORS")

    if not os.path.exists(co2_result_target_dir):
        os.makedirs(co2_result_target_dir)
    if not os.path.exists(co2_error_target_dir):
        os.makedirs(co2_error_target_dir)

    # Target paths
    co2_result_target = os.path.join(co2_result_target_dir, co2_result_name)
    co2_error_target = os.path.join(co2_error_target_dir, co2_error_name)

    # Move files
    shutil.move(src=co2_result, dst=co2_result_target)
    shutil.move(src=co2_error, dst=co2_error_target)

    # Print info
    print("Moved: %s ==> %s" % (co2_result, co2_result_target))
    print("Moved: %s ==> %s" % (co2_error, co2_error_target))


