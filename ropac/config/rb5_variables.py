import os
import yaml
#import pprint

current_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file = os.path.join(current_dir, 'rb5_radar_info.yaml')

with open(yaml_file, 'r') as f:
    rb5_fixed_var = yaml.load(f, Loader=yaml.FullLoader)