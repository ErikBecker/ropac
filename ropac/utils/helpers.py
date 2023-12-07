

import glob
import multiprocessing
import os
import re
import sys

from collections import defaultdict
from datetime import datetime

from ropac.config.radar_variables import radar_info


def pid_check(pid_file, logger):
    
    def read_pid_file():
        logger.debug(f"Reading PID file: {pid_file_path}")
        with open(pid_file_path, "r") as f:
            pid = f.read().strip()
        return pid
    
    def write_pid_file(pid):
        logger.debug(f"Writing PID file: {pid_file_path}")
        with open(pid_file_path, "w") as f:
            f.write(pid)
    
    current_pid = str(os.getpid())
    pid_file_path = pid_file.split('.')[0] + '.pid'
    
    if os.path.exists(pid_file_path):
        previous_pid = read_pid_file()

        if os.path.exists(f"/proc/{previous_pid}"):
            logger.debug(f"Process with PID {previous_pid} is already running, exiting.")
            sys.exit(1)
            
    write_pid_file(current_pid)
   


# def find_files(directory: str, extension: str):
    
#     """_summary_

#     Finds all files in the directory with the given extension

#     Args:
#         directory (str): specify the directory to search
#         extension (str): specify the directory to search

#     Returns:
#         files (list): A list of files with given extension
#     """    

#     pattern = f"{directory}/**/*{extension}"
#     files = glob.glob(pattern, recursive=True)
#     if len(files) == 0:
#         raise ValueError(f"No files found with extension {extension} in directory {directory}")
        
#     files = [x for x in files if os.path.isfile(x)]

#     return files

def id_radar(infile):
    
    radar_id = None
    
    for radar in radar_info:
        if radar_info[radar]['type'] == 'gdrx':
            if radar_info[radar]['name'] in infile or radar_info[radar]['name'].lower() in infile or radar in infile:
                radar_id = radar_info[radar]['id']
                break
    
    if radar_id == None: raise ValueError("Cannot ID radar data!!!")
    
    return radar

def group_rb5_files(fileList: list):
    
    file_groups = defaultdict(dict)
    
    for rfile in fileList:
        
        radar_id = id_radar(rfile)

        match = re.search(r'\d{16}', rfile)
        if match:
            timestamp_str = match.group()
            timestamp = datetime.strptime(timestamp_str[:-2], '%Y%m%d%H%M%S')
            if timestamp in file_groups[radar_id]:
                file_groups[radar_id][timestamp].append(rfile)
            else:
                file_groups[radar_id][timestamp] = [rfile]
        
    return file_groups


def group_scn_files(fileList: list):
    
    group = defaultdict(dict)
    
    for scnfile in fileList:
        scn_name = scnfile.split('/')[-1]
        radar_name = scn_name.split('_')[0]
        scn_date = scn_name.split('_')[1]
        scn_time = scn_name.split('_')[2]
        scn_dt = scn_date+scn_time
        scn_dt = datetime.strptime(scn_dt, "%Y%m%d%H%M%S")
        
        group[radar_name][scn_dt] = group[radar_name].get(scn_dt, []) + [scnfile]

        
    return group

    
def group_odim_files(fileList: list):
    
    file_groups = defaultdict(lambda: defaultdict(dict))
    
    for rfile in fileList:
        
        radar_id = rfile.split('/')[-1].split('.')[0]
        timestamp = datetime.strptime(rfile.split('/')[-1].split('.')[1],'%Y%m%d_%H%M%S')
        product = rfile.split('/')[-1].split('.')[2]
        file_groups[radar_id][product].setdefault(timestamp, rfile)
            
    return file_groups


def are_all_files(file_list):
    for file_path in file_list:
        if not os.path.isfile(file_path):
            return False
    return True




def find_files(directory, extension):
    files = []
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith(extension):
            files.append(entry.path)
        elif entry.is_dir():
            files.extend(find_files(entry.path, extension))
    return files

def search_directories(root_directory, extension):
    pool = multiprocessing.Pool()
    results = []
    for root, dirs, files in os.walk(root_directory):
        for directory in dirs:
            results.append(pool.apply_async(find_files, args=(os.path.join(root, directory), extension)))
    pool.close()
    pool.join()
    files = []
    for result in results:
        files.extend(result.get())

    return set(files)


def find_index_greater_than(lst, setmax):
    for i in range(len(lst)):
        if lst[i] > setmax:
            return i
    return -1 
