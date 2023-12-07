
import os
import yaml
#import pprint

current_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file = os.path.join(current_dir, 'metadata.yaml')

with open(yaml_file, 'r') as f:
    fixed_metadata = yaml.load(f, Loader=yaml.FullLoader)