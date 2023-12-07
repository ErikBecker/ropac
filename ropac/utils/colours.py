#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 16:19:41 2023

@author: ebecker
"""

import os
import yaml
#import pprint

current_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file = os.path.join(current_dir,'colour_maps.yaml')

with open(yaml_file, 'r') as f:
    cmap = yaml.load(f, Loader=yaml.FullLoader)

def get_colour_map(quantity):
    
    if quantity=='RATE':
        return cmap['jet']
    elif quantity=='TH':
        return cmap['reflectivity']
    elif quantity=='DBZH':
        return cmap['reflectivity']
    elif quantity=='TV':
        return cmap['reflectivity']
    elif quantity=='DBZV':
        return cmap['reflectivity']
    elif quantity=='DBZH_CLEAN':
        return cmap['reflectivity']
    elif quantity=='DBZV_CLEAN':
        return cmap['reflectivity']
    elif quantity=='VRADH':
        return cmap['velocity']
    elif quantity=='VRADDH':
        return cmap['velocity']
    elif quantity=='ZDR':
        return cmap['ZDR']
    elif quantity=='KDP':
        return cmap['KDP']
    elif quantity=='PHIDP':
        return cmap['PhiDP']
    elif quantity=='SPHIDP':
        return cmap['PhiDP']
    elif quantity=='RHOHV':
        return cmap['RhoHV']
    elif quantity=='WRADH':
        return cmap['SpWidth']
    elif quantity=='QIND':
        return cmap['cyan']
    elif quantity=='SNRH':
        return cmap['cyan']
    # elif quantity=='CLASS':
    #     return cmap['PID_3DRapic']
    else:
        return cmap['greyscale']




















