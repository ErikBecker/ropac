#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 10:43:02 2023

@author: ebecker
"""

from ropac import Elevation
from ropac import Moment
from ropac import radar_config

from ropac.iofiles.read_rb5_data import read_file_list
from ropac.config.polar_metadata import TopHow, TopWhat, TopWhere


from datetime import datetime, timedelta

import numpy as np

def quantity_mapping(quantity):
    rb5_to_odim = {'dBZ': 'DBZH', 'dBuZ': 'TH', 'dBZv': 'DBZV', 'dBuZv': 'TV', 'V': 'VRADH', 'ZDR': 'ZDR',
                    'KDP': 'KDP','PhiDP': 'PHIDP' ,'uPhiDP': 'SPHIDP','RhoHV': 'RHOHV','W': 'WRADH'}
    return rb5_to_odim[quantity]

def return_sensor_info(dataset,key):
    
    var_list = [data[key] for _,data in dataset.items()]
    if not all(var == var_list[0] for var in var_list):
        raise ValueError(f"All variables {key} are not the same")
    return var_list[0]

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

def return_slice_info(dataset):
    var_list = [data['scan'] for _,data in dataset.items()]
    inverted_dict = invert_dict(var_list)
    slices = inverted_dict.pop('slice')
    inverted_dict = simplify_similar_lists(inverted_dict)
    return slices, inverted_dict

def add_metadata_from_config(how,meta):
    for key in meta:
        if not isinstance(meta[key], list):
            how.add_attribute(key, meta[key])

def add_metadata_from_rainbow(elev,meta,i):
    for key in meta:
        if key not in ['@refid', 'dynz', 'dynv', 'dynw', 'dynzdr', 'dynldr', 'dynkdp', 'dynsnr', 'gdrxanctxfreq'] and meta[key] is not None:
            if not isinstance(meta[key], list):
                elev.how.add_attribute(f'rb5_{key.replace("@","")}', meta[key])
            else:
                elev.how.add_attribute(f'rb5_{key.replace("@","")}', meta[key][i])

def add_metadata_rb5_slice_info(how,meta):
    for key in meta:
        how.add_attribute(f'rb5_{key.replace("@","")}', meta[key])

def get_data_object(ftype):
    if ftype == 'azi': 
        return 'AZIM'
    if ftype == 'vol': 
        return 'PVOL'
    raise ValueError("This is an unknown RB5 file type", ftype)

def get_radar_config(place):
    for radar_name in radar_config:
        if radar_name.lower() in place.lower():
            return radar_config[radar_name]
    raise ValueError("Radar name not in config directory", place)

def get_rayinfo(rayinfo):

    if isinstance(rayinfo, list) and len(rayinfo)==2:
        my_dict = {index: value for index, value in enumerate(rayinfo)}
        rayinfo = my_dict

    if 0 in rayinfo:
        if rayinfo[0]['@refid'] == 'startangle':
            angledepth = float(rayinfo[0]['@depth'])
            nrays = float(rayinfo[0]['@rays'])
            startangle = rayinfo[0]['data'] * (nrays/2**angledepth)
        else:
            startangle = None

    if 1 in rayinfo:
        if rayinfo[1]['@refid'] == 'stopangle':
            angledepth = float(rayinfo[1]['@depth'])
            nrays = float(rayinfo[1]['@rays'])
            stopangle = rayinfo[1]['data'] * (nrays/2**angledepth) 
        else:
            stopangle = None
    
    if '@refid' in rayinfo:
        if rayinfo['@refid'] == 'startangle':
            angledepth = float(rayinfo['@depth'])
            nrays = float(rayinfo['@rays'])
            startangle = rayinfo['data'] * (nrays/2**angledepth) 
            stopangle = None

    return startangle, stopangle

def get_roll(in_array):
    return in_array.shape[0] - np.argmax(in_array) - 1

def calculate_NI(highprf,lowprf,wavelength):
    if lowprf==0:
        return ((wavelength/100)/4) * highprf
    return ((wavelength/100)/4) * highprf * (lowprf/(highprf-lowprf))

def set_astart(azi_start):
    if azi_start[0] > 180: 
        return round(azi_start[0] - 360,3)
    return round(azi_start[0],3)

def get_sweep_info(moment_data):
    
    slicedata = []
    metadata = {}
    
    for ie, sweep in enumerate(moment_data):
        slicedata.append(sweep.pop('slicedata'))
        for key,value in sweep.items():
            metadata.setdefault(key, []).append(value)
    
    for key,value in metadata.items():
        test = all(var == value[0] for var in value)
        if test:
            metadata[key] =  value[0]
            
    return slicedata, metadata

def get_slice_info(slices,what_object):
    slicedata = []
    elev_meta = []
    for moment in slices:
        if what_object == 'AZIM': moment = [moment]
        sld, elm = get_sweep_info(moment)
        slicedata.append(sld)
        elev_meta.append(elm)
    inverted_dict = invert_dict(elev_meta)
    inverted_dict = simplify_similar_lists(inverted_dict)
    return slicedata, inverted_dict

def get_elev_metadata(elev_meta,key,i):
    if isinstance(elev_meta[key],list):
        return elev_meta[key][i]
    return elev_meta[key]

def get_scan_times(timestamp,antspeed,sensor):
    
    if sensor=='drx':
        endtime = timestamp
        td = 360 / antspeed
        starttime = endtime - timedelta(seconds=td)
    else:
        starttime = timestamp
        td = 360 / antspeed
        endtime = starttime + timedelta(seconds=td)
    
    return starttime, endtime
        
    
def convert_rb5(rb5files: list):
    
    dataset = read_file_list(rb5files)
    try:
        sensorinfo = return_sensor_info(dataset,'sensorinfo')
    except:
        sensorinfo = return_sensor_info(dataset,'radarinfo')
        sensorinfo['@name'] = sensorinfo.pop('name')
        sensorinfo['@type'] = 'N/A'
        sensorinfo['alt'] = sensorinfo.pop('@alt')
        sensorinfo['lat'] = sensorinfo.pop('@lat')
        sensorinfo['lon'] = sensorinfo.pop('@lon')


    sensorinfo['version'] = return_sensor_info(dataset,'@version')
    sensorinfo['type'] = return_sensor_info(dataset,'@type')
    sensorinfo['owner'] = return_sensor_info(dataset,'@owner') 
    sensorinfo['PLC'] = sensorinfo.pop('@name')
    sensorinfo['sensor'] = sensorinfo.pop('@type')
    sensorinfo['rb5_id'] = sensorinfo.pop('@id')
    
    slices, slice_info = return_slice_info(dataset)
    slice_info['scan_name'] = slice_info.pop('@name')
    pargroup = slice_info.pop('pargroup')
    
    radar_metadata = get_radar_config(sensorinfo['PLC'])
    
    # where
    where = TopWhere()
    where.height = float(sensorinfo.pop('alt'))
    where.lat = float(sensorinfo.pop('lat'))
    where.lon = float(sensorinfo.pop('lon'))
        
    # how
    how = TopHow()
    how.wavelength = float(sensorinfo.pop('wavelen')) * 100
    how.beamwidth = float(sensorinfo.pop('beamwidth'))
    how.add_attribute('software', 'RAINBOW')
    how.add_attribute('sw_version', sensorinfo.pop('version'))
   
    #what
    what = TopWhat()
    timestamp = datetime.strptime(f'{slice_info.pop("@date")} {slice_info.pop("@time")}',"%Y-%m-%d %H:%M:%S")
    what.date = timestamp.strftime("%Y%m%d")
    what.time = timestamp.strftime("%H%M%S")
    what.object = get_data_object(sensorinfo.pop('type'))
    what.source = f'PLC:{sensorinfo.pop("PLC")},CMT:{";".join([f"{key}={value}" for key, value in sensorinfo.items()])};id={radar_metadata["id"]}'
        
    add_metadata_from_config(how,radar_metadata)
    add_metadata_rb5_slice_info(how,slice_info)
    
    slicedata, elev_meta = get_slice_info(slices,what.object)
    
    elev = [Elevation() for _ in elev_meta['@refid']]
    
    for im, moment in enumerate(slicedata):
        for ie, sweep in enumerate(moment):
            
            rawdata = sweep.pop('rawdata')
            
            #get variables
            timestamp = datetime.strptime(f'{sweep.pop("@date")} {sweep.pop("@time")}',"%Y-%m-%d %H:%M:%S")
            antspeed = float(get_elev_metadata(elev_meta,'antspeed',ie)) 
            pw_index = int(get_elev_metadata(elev_meta,'pw_index',ie)) 
            startangle, stopangle = get_rayinfo(sweep.pop('rayinfo'))
            a1gate = startangle[0]
            roll = get_roll(startangle)
            starttime, endtime = get_scan_times(timestamp,antspeed,sensorinfo['sensor'].lower())
            # stime.append(starttime)
            
            # Roll azi rays to north start
            startangle = np.roll(startangle, roll)
            
            #dataset.where
            elev[ie].where.a1gate = int(np.where(startangle == a1gate)[0][0])
            elev[ie].where.elangle = float(get_elev_metadata(elev_meta,'posangle',ie)) 
            elev[ie].where.nbins = int(rawdata.pop('@bins'))
            elev[ie].where.nrays = int(rawdata.pop('@rays'))
            elev[ie].where.rscale = float(get_elev_metadata(elev_meta,'rangestep',ie)) * 1000
            elev[ie].where.rstart = float(get_elev_metadata(elev_meta,'start_range',ie))
            # print(elev[ie].where)
            
            #dataset.how
            elev[ie].how.highprf = float(get_elev_metadata(elev_meta,'highprf',ie))
            elev[ie].how.lowprf = float(get_elev_metadata(elev_meta,'lowprf',ie))
            elev[ie].how.CSR = float(get_elev_metadata(elev_meta,'csr',ie)) 
            elev[ie].how.LOG = float(get_elev_metadata(elev_meta,'sqi',ie)) 
            elev[ie].how.SQI = float(get_elev_metadata(elev_meta,'log',ie)) 
            elev[ie].how.NEZH = float(get_elev_metadata(elev_meta,'noise_power_dbz',ie))  
            if 'noise_power_dbz_dpv' in elev_meta: elev[ie].how.NEZV = float(get_elev_metadata(elev_meta,'noise_power_dbz_dpv',ie))
            elev[ie].how.NI = calculate_NI(elev[ie].how.highprf, elev[ie].how.lowprf, how.wavelength)
            elev[ie].how.astart = set_astart(startangle)
            elev[ie].how.pulsewidth = radar_metadata['pulsewidth'][pw_index]
            elev[ie].how.radconstH = float(get_elev_metadata(elev_meta,'rspdphradconst',ie).split(' ')[pw_index]) 
            elev[ie].how.radconstV = float(get_elev_metadata(elev_meta,'rspdpvradconst',ie).split(' ')[pw_index])   
            elev[ie].how.rpm = 60 / (360 / antspeed)
            elev[ie].how.scan_index = ie + 1
            elev[ie].how.startazA = startangle

            if stopangle is not None:
                stopangle = np.roll(stopangle, roll)
                elev[ie].how.stopazA = stopangle

            if 'zdrcal' in radar_metadata:
                elev[ie].how.zdrcal = radar_metadata['zdrcal'][pw_index]

            add_metadata_from_rainbow(elev[ie],elev_meta,ie)
            # print(elev[ie].how)
            
            # dataset.what
            elev[ie].what.endtime = endtime.strftime("%H%M%S")
            elev[ie].what.enddate = endtime.strftime("%Y%m%d")
            elev[ie].what.product = 'SCAN'
            elev[ie].what.startdate = starttime.strftime("%Y%m%d")
            elev[ie].what.starttime = starttime.strftime("%H%M%S")
            # print(elev[ie].what)
            
            # unpack dataset.data.what                        
            datamin = float(rawdata.pop('@min'))
            datamax = float(rawdata.pop('@max'))
            datadepth = float(rawdata.pop('@depth'))
            
            mom = Moment()
            mom.what.gain = (datamax - datamin) / (2**datadepth - 2)
            mom.what.offset = datamin - mom.what.gain
            mom.what.undetect = 0.
            mom.what.nodata = 0.
            mom.what.quantity = quantity_mapping(rawdata.pop('@type'))
            mom.data = np.roll(rawdata.pop('data'),roll,axis=0)
            # print(mom.what)
            elev[ie].data.append(mom)
            
            # print( mom.what.quantity,elev[ie].where.elangle)
            
    
    return (elev,what,where,how)
    

 
    
if __name__ == "__main__":

    import os
    from ropac import system_config as cfg
    
    # vol_file = os.path.join(cfg.path.ingest,'2013051000000600dBZ.vol')
    vol_file = os.path.join(cfg.path.ingest,'2019100100000700dBZ.vol')

    print(vol_file)
    convert_rb5([vol_file])



