   
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 03:50:27 2023

@author: ebecker
"""

from collections import namedtuple

import numpy as np

from ropac import Elevation
from ropac import Moment

from ropac import radar_config
from ropac.config.polar_metadata import TopHow, TopWhat, TopWhere
from ropac.config.scn_variables import scn_fixed_var
from ropac.iofiles.read_scn_data import read_scn_file_list

from datetime import datetime, timedelta

ScanInfo = namedtuple('ScanInfo', ['name', 'date', 'time', 'elevation_number', 'scn_method'])

def set_check(input_list):
    if len(set(input_list)) == 1:
        return input_list[0]
    return input_list

def parse_scn_name(scn_vol):
    name, date, time, elevation_number, scn_method = [], [], [], [], []
    for scn_name in scn_vol:
        rn, dt, tm, elnum, method = scn_name.split('/')[-1].split('.')[0].split('_')
        name.append(rn)
        date.append(dt)
        time.append(tm)
        elevation_number.append(elnum)
        scn_method.append(method)
    return ScanInfo(set_check(name), set_check(date), set_check(time), set_check(elevation_number), set_check(scn_method))

def get_radar_config(furuno_name):
    for radar_name in radar_config:
        if 'name' in list(radar_config[radar_name].keys()):
            if furuno_name == radar_config[radar_name]['name']:
                return radar_config[radar_name].copy()
    raise ValueError("Radar name not in config directory | check furuno_name config value", furuno_name)

def get_azim_angles(scn_ray_info):
    return [item['azimuth_start'] for key, item in scn_ray_info.items()]

def find_most_common(in_array, length):
    
    values = in_array[0]
    counter = in_array[1]
    fraction = [count/length for count in counter]
    
    if np.max(fraction) > 0.98:
        return values[np.argmax(fraction)]
    raise ValueError("Elevation angles less than the 98% fraction limit")
    

def get_elev_angles(scn_ray_info):
    ele = [item['elevation'] for key, item in scn_ray_info.items()]
    count_unique = np.unique(ele,return_counts=True)
    elevation = find_most_common(count_unique, len(ele))
    return elevation


def get_azim_offset(radar_info,scn_header):
    # print(radar_info['override_azoffset'],type(radar_info['override_azoffset']))
    if radar_info['override_azoffset']:
        # print('here i am',)
        return radar_info['Azimuth_Offset']
    return scn_header['Azimuth_Offset']

def apply_offset(azi,Azimuth_Offset):
    azi_start = list(map(lambda x:x+Azimuth_Offset, azi))    
    azi_start = [round(x % 360,3) for x in azi_start]
    azi_stop = azi_start[1:] + [azi_start[0]]  
    return np.array(azi_start), np.array(azi_stop)

def get_roll(in_array):
    return in_array.shape[0] - np.argmax(in_array) 

def set_astart(azi_start):
    if azi_start[0] > 180: 
        return round(azi_start[0] - 360,3)
    return round(azi_start[0],3)

def get_starttime(scn_header):
    stime = datetime(scn_header.pop('UTC_time_year'),
                    scn_header.pop('UTC_time_month'),
                    scn_header.pop('UTC_time_day'),
                    scn_header.pop('UTC_time_hour'),
                    scn_header.pop('UTC_time_minute'),
                    scn_header.pop('UTC_time_second'))
    return stime

def invert_dict(var_list):
    invert_dict = {}
    for d in var_list:
        for key, value in d.items():
            if key not in invert_dict:
                invert_dict[key] = [value]
            else:
                invert_dict[key].append(value)
    return invert_dict

def simplify_similar_lists(input_dict):
    for key in input_dict:
        test = [var == input_dict[key][0] for var in input_dict[key]]
        if all(test):
            input_dict[key] = input_dict[key][0]
    return input_dict

def parse_header_info(scn_volume):
    scn_header = []
    for scn_name in scn_volume:
        scn_header.append(scn_volume[scn_name]['header'])
    scn_header = invert_dict(scn_header)
    scn_header = simplify_similar_lists(scn_header)
    return scn_header


def get_data_object(length):
    if length == 1: 
        return 'AZIM'
    if length > 1: 
        return 'PVOL'
    raise ValueError("SCN volume length is 0", length)

def coord_to_decimal(degree,minute,second):
    return round(degree + minute / 60 + second / 3600, 5)

def add_metadata_from_config(how,meta):
    for key in meta:
        if not isinstance(meta[key], list):
            how.add_attribute(f'scn_{key}', meta[key])

def add_metadata_from_header(how,meta):
    for key in meta:
        if key not in ['PRF1', 'PRF2'] and 'time' not in key:
            if not isinstance(meta[key], list):
                how.add_attribute(f'scn_{key}', meta[key])

def calculate_NI(highprf,lowprf,wavelength):
    if lowprf==0:
        return ((wavelength/100)/4) * highprf
    return ((wavelength/100)/4) * highprf * (lowprf/(highprf-lowprf))            

def get_pulsewidth(pulse_info,highprf, lowprf, rscale):
    
    test1 = pulse_info.pop('highprf')
    test2 = pulse_info.pop('lowprf')
    # test3 = pulse_info.pop('rscale')
    
    if test1 == highprf and  test2 == lowprf: #and  test3 == rscale:
        return pulse_info.pop('pulsewidth')
    
    raise ValueError(f'pulse_info does not match file metadata. Check prf_pattern and pulse_set in config file prf high={test1} low={test2}')
    

def convert_scn(scn_files):  
    
    scn_volume = read_scn_file_list(sorted(scn_files))
    scn_info = parse_scn_name(scn_volume)
    scn_header = parse_header_info(scn_volume)
    radar_info = get_radar_config(scn_info.name)
    # print(scn_info)
    # print(radar_info)
    # print(f"AZI at start = {radar_info['Azimuth_Offset']} - {radar_info['name']}")
    if 'model' in radar_info:
        model = radar_info['model']
        if model=='WR2120': pw_index = f"{radar_info['prf_pattern']}-{scn_header['Tx_pulse_specification']}"
        elif model=='WR2100': pw_index = scn_header['Tx_pulse_specification']
    else:
        pw_index = scn_header['Tx_pulse_specification']
    
    # # what
    what = TopWhat()
    what.date = scn_info.date
    what.object = get_data_object(len(scn_volume)) 
    what.source = f'PLC:{radar_info.pop("name")},CMT:id={radar_info.pop("id")}' 
    what.time = scn_info.time 
    # print(what)
    
    # where
    where = TopWhere()
    if "height" in radar_info:
        where.height = radar_info.pop("height")
    else:
        where.height = scn_header.pop("Altitude_cm") / 100
    where.lat = coord_to_decimal(scn_header.pop('Latitude_degree'),scn_header.pop('Latitude_minute'),scn_header.pop('Latitude_second'))
    where.lon = coord_to_decimal(scn_header.pop('Longitude_degree'),scn_header.pop('Longitude_minute'),scn_header.pop('Longitude_second'))
    # print(where)
    
    #how
    how = TopHow()
    how.wavelength = radar_info.pop('wavelength')
    how.beamwidth = radar_info['beamwH']
    how.add_attribute('system',  radar_info.pop('system'))
    how.add_attribute('antgainH', radar_info.pop('antgainH'))
    how.add_attribute('antgainV', radar_info.pop('antgainV'))
    how.add_attribute('poltype', radar_info.pop('poltype'))
    how.add_attribute('beamwH', radar_info.pop('beamwH'))
    how.add_attribute('beamwV', radar_info.pop('beamwV'))
    how.add_attribute('RXgainH', radar_info.pop('RXgainH'))
    how.add_attribute('RXgainV', radar_info.pop('RXgainV'))
    how.add_attribute('gasattn', radar_info.pop('gasattn'))
    how.scan_count = len(scn_volume)
    # print(f"AZI at meta = {radar_info['Azimuth_Offset']}")
    add_metadata_from_config(how,radar_info)
    add_metadata_from_header(how,scn_header)
    # print(how)
    # print(scn_header)
    
    elev = [Elevation() for _ in range(len(scn_volume))]
    
    # print(f"AZI at for loop = {radar_info['Azimuth_Offset']}")

    for ie, scn_name in enumerate(scn_volume):
        
        scn_moments = scn_volume[scn_name]['data']
        scn_header = scn_volume[scn_name]['header']
        scn_ray_info = scn_volume[scn_name]['ray_info']
        if 'model' in locals():
            pulse_info = scn_fixed_var['pulse_settings'][model][pw_index].copy()
        else:
            pulse_info = scn_fixed_var['pulse_settings']['NONE'][1].copy()
        # print(scn_header)
        
        # unpack azimuth angle info      
        azi = get_azim_angles(scn_ray_info)
        ele = get_elev_angles(scn_ray_info)
        # print(radar_info)
        Azimuth_Offset = get_azim_offset(radar_info,scn_header)
        # print(f"{what.source} Azi Offset = {Azimuth_Offset}")
        azi_start, azi_stop = apply_offset(azi,Azimuth_Offset)
        a1gate = azi_start[0]
        roll = get_roll(azi_start)
        
        # Roll azi rays to north start
        azi_start = np.roll(azi_start, roll)
        azi_stop = np.roll(azi_stop, roll)        

        rpm = scn_header.pop('Antenna_rotation_speed_rpm')
        
        # scan starttime
        start_time = get_starttime(scn_header)
        end_time = start_time + timedelta(seconds=(60 / rpm))
        
        # dataset.where infor 
        elev[ie].where.a1gate = int(np.where(azi_start == a1gate)[0][0])
        elev[ie].where.elangle = ele
        elev[ie].where.nbins = scn_header.pop('number_of_range_bins')
        elev[ie].where.nrays = scn_header.pop('number_of_sweeps')
        elev[ie].where.rscale = scn_header.pop('range_resolution_m')
        elev[ie].where.rstart = 0.0
        # print(elev[ie].where)
        
        #dataset.how
        elev[ie].how.highprf = scn_header.pop('PRF1')
        elev[ie].how.lowprf = scn_header.pop('PRF2')
        elev[ie].how.NI = calculate_NI(elev[ie].how.highprf, elev[ie].how.lowprf, how.wavelength)
        elev[ie].how.astart = set_astart(azi_start)
        # elev[ie].how.pulsewidth = get_pulsewidth(pulse_info,elev[ie].how.highprf, elev[ie].how.lowprf,elev[ie].where.rscale)
        elev[ie].how.pulsewidth = pulse_info.pop('pulsewidth')
        elev[ie].how.radconstH = scn_header.pop('radar_constant_H')
        elev[ie].how.radconstV = scn_header.pop('radar_constant_V')
        elev[ie].how.rpm = rpm
        elev[ie].how.scan_index = ie + 1
        elev[ie].how.startazA = azi_start
        elev[ie].how.stopazA = azi_stop
        add_metadata_from_config(elev[ie].how, pulse_info)
        add_metadata_from_header(elev[ie].how, scn_header)
        # print(elev[ie].how)
        
        # dataset.what
        elev[ie].what.endtime = end_time.strftime("%H%M%S")
        elev[ie].what.enddate = end_time.strftime("%Y%m%d")
        elev[ie].what.product = 'SCAN'
        elev[ie].what.startdate = start_time.strftime("%Y%m%d")
        elev[ie].what.starttime = start_time.strftime("%H%M%S")
        # print(elev[ie].what)
        
        offset = scn_fixed_var['offset']
        gain = scn_fixed_var['gain']
        undetect = scn_fixed_var['undetect']
        nodata = scn_fixed_var['nodata']
        quantity = scn_fixed_var['quantity_mapping']
        
        # loop through moment data
        for moment in scn_moments:
            mom = Moment()
            mom.what.gain = gain[moment]
            mom.what.offset = offset[moment]
            mom.what.undetect = undetect[moment]
            mom.what.nodata = nodata[moment]
            mom.what.quantity = quantity[moment]
            mom.data = np.roll(np.array((scn_moments[moment] - offset[moment]) / gain[moment],dtype=np.uint16),roll,axis=0)
            # print(mom.what)
            elev[ie].data.append(mom)
            
    return (elev,what,where,how)   
        


        
    

    
    
    
    
    
    
    
    