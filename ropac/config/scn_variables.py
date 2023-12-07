#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 01:30:32 2023

@author: ebecker
"""

import os
import yaml
#import pprint

current_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file = os.path.join(current_dir, 'scn_radar_info.yaml')

with open(yaml_file, 'r') as f:
    scn_fixed_var = yaml.load(f, Loader=yaml.FullLoader)

#pprint.pprint(scn_fixed_var)





























