import os
import yaml

def load_radar_config(file_paths):
    radar_config = {}
    for file_path in file_paths:
        radar_name = os.path.basename(file_path).split('.')[0]
        with open(file_path, 'r') as yaml_file:
            config_data = yaml.safe_load(yaml_file)
        radar_config[radar_name] = config_data
    return radar_config

