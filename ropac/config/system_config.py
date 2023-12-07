import os
import yaml
from dataclasses import dataclass

@dataclass
class Paths:
    logs: str
    data: str
    images: str
    stats: str
    ingest: str

@dataclass
class Logs:
    level: str
    output: str

@dataclass
class SystemConfig:
    system_log_level: Logs
    log_level: Logs
    path: Paths

def load_sys_config(file_path):

    with open(file_path, 'r') as yaml_file:
        config_data = yaml.safe_load(yaml_file)

    # Replace $HOME with actual home directory
    if 'directories' in config_data:
        for path in config_data['directories']:
            config_data['directories'][path] = os.path.expanduser(config_data['directories'][path])

    
    path_data = config_data.get('directories', {})
    logging_data = config_data.get('logging-settings', {})
    
    paths = Paths(
        logs=path_data.get('logs', ''),
        data=path_data.get('data', ''),
        images=path_data.get('images', ''),
        stats=path_data.get('stats', ''),
        ingest=path_data.get('ingest', '')
    )
    
    log_level = Logs(
        level=logging_data.get('log_level', ''),
        output=logging_data.get('output_level', '')
    )
    
    system_log_level = Logs(
        level=logging_data.get('system_log_level', ''),
        output=logging_data.get('system_output_level', '')
    )
    
    system_config = SystemConfig(
        system_log_level=system_log_level,
        log_level=log_level,
        path=paths
    )
    
    return system_config

# # Specify the path to your YAML file
# yaml_file_path = 'config.yaml'  # Update with your file path

# # Read the YAML file and populate the data classes
# config = read_config_from_yaml(yaml_file_path)

# # Access the data in the data classes
# print(config.system_log_level.level)
# print(config.path.data)
