__author__ = 'hentenka'
import os, sys

def filePathsToList(source_dir, criteria, fileformat):
    flist = []
    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if criteria in filename and filename.endswith(fileformat):
                flist.append(os.path.join(root, filename))
    return flist

def createMatrixFolder(to_id):
    dirname = "%sxxx" % str(to_id)[:4]
    fullpath = os.path.join(outDir, dirname)
    if not os.path.isdir(fullpath):
        os.makedirs(fullpath)
    return fullpath

def findMatchingFile(Source_fp, targetPaths, mode='pt'):
    search_folder = os.path.dirname(targetPaths[0])
    Source_ID = os.path.basename(Source_fp).split('_')[0]
    for targetfile in targetPaths:
        if mode == 'car':
            target_ID = os.path.basename(targetfile).split('_')[2]
        else:
            target_ID = os.path.basename(targetfile).split('_')[0]
        if target_ID == Source_ID:
            return targetfile
    print("Error: Could not find corresponding target_file for %s in %s" % (Source_ID, search_folder))
    sys.exit()
