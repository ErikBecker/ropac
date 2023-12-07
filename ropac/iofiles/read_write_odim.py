#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 07:21:41 2020

@author: - Erik Becker
"""

import h5py
import os

import shutil
import string
import tempfile

import numpy as np

def get_h5_groups(h5f):
    """ Gets the group name structure of hdf5 file.

    Parameters
    ----------
    h5f : h5py._hl.files.File 
        DESCRIPTION:
            An open h5py.File() object

    Returns
    -------
    group : list(str)
        DESCRIPTION:
            The group names as a list of strings
    """

    def extract(name,node):
        group_list.append(name)
        return None        
    
    group = ['/']
    group_list = []           
    
    h5f.visititems(extract)

    for grp in group_list:
        group.append('/' + grp)

    return group  
        
def get_h5_attr(h5f,groups):
    """Gats the hdf5 file attribute names and values.
    
    Parameters
    ----------
    h5f : h5py._hl.files.File 
        DESCRIPTION:
            An open h5py.File() object
    groups : list(str)
        DESCRIPTION:
            The group names as a list of strings
        
    Returns
    -------
    attr : dict(dict)
        DESCRIPTION:
            A dictionary with group names as keys and values as dictionaries 
            containing attribute names as keys and values.

    """

    attr = {}

    for key in groups:
        
        group = h5f[key]
        AttDict = {}
        
        for att in group.attrs:
            value = group.attrs[att]
            if isinstance(value, np.ndarray):
                if len(value)==1:
                    AttDict[att] = value[0]
                else:
                    AttDict[att] = value
            elif isinstance(value, np.bytes_):
                AttDict[att] = value.decode('utf-8')
            else:
                AttDict[att] = value
            # print(att,value,AttDict[att])
            
        attr[key] = AttDict
            
    return attr
    
def get_h5_data(h5f,groups):
    """Gets the data in hdf5 file
    
    Parameters
    ----------
    h5f : h5py._hl.files.File 
        DESCRIPTION:
            An open h5py.File() object
    groups : list(str)
        DESCRIPTION:
            The group names as a list of strings

    Returns
    -------
    data : dict
        DESCRIPTION.
            A dictionary of numpy arrays

    """

    data = {}

    for group in groups:

        try:
            raw = h5f[group][()]
            data[group] = raw
        except:
            continue

    return data
    
    
def read_odim(filename):
    """Reads hdf5 file and returns file data and attributes

    Parameters
    ----------
    filename : str
        DESCRIPTION.
        A str containing the hdf5 file name.

    Returns
    -------
    data : dict
        DESCRIPTION.
            A dictionary of numpy arrays
    attr : dict(dict)
        DESCRIPTION:
            A dictionary with group names as keys and values as dictionaries 
            containing attribute names as keys and values.

    """
      
    h5f = h5py.File(filename, 'r')
        
    groups = get_h5_groups(h5f)
    attr = get_h5_attr(h5f,groups)
    data = get_h5_data(h5f,groups)     
    
    h5f.close()
    
    return data, attr


def create_groups(h5f,groups):
    """
    

    Parameters
    ----------
    h5f : TYPE
        DESCRIPTION.
    groups : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    for group in sorted(groups):
        if not group.endswith('data') and not group == '/':
            h5f.create_group(group)

def write_attr(h5f,attr):
    """
    

    Parameters
    ----------
    h5f : TYPE
        DESCRIPTION.
    attr : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    for item in attr:
        group = h5f[item]

        for att in attr[item]:
            
        
            # print(att,attr[item][att],type(attr[item][att]))
            if not attr[item][att] is None:
                # print(att,attr[item][att],type(attr[item][att]),attr[item][att] is None)
                if isinstance(attr[item][att], np.bytes_):
    
                    tid = h5py.h5t.C_S1.copy()
                    tid.set_size(len(attr[item][att])+1)
                    tid.set_strpad(h5py.h5t.STR_NULLTERM)
                    H5T_C_S1 = h5py.Datatype(tid)
    
                    group.attrs.create(att, attr[item][att].astype(H5T_C_S1), dtype=H5T_C_S1)
                        
                elif isinstance(attr[item][att], bytes):
                   
                    tid = h5py.h5t.C_S1.copy()
                    tid.set_size(len(attr[item][att])+1)
                    tid.set_strpad(h5py.h5t.STR_NULLTERM)
                    H5T_C_S1 = h5py.Datatype(tid)
    
                    group.attrs.create(att, np.char.encode(attr[item][att].decode()).astype(H5T_C_S1), dtype=H5T_C_S1)
                    
                elif isinstance(attr[item][att], str):
                    
                    
                    tid = h5py.h5t.C_S1.copy()
                    tid.set_size(len(attr[item][att])+1)
                    tid.set_strpad(h5py.h5t.STR_NULLTERM)
                    H5T_C_S1 = h5py.Datatype(tid)
    
                    group.attrs.create(att, np.char.encode(attr[item][att]).astype(H5T_C_S1), dtype=H5T_C_S1)
                    
                else:
                    group.attrs[att] = attr[item][att]
                
                
            

def write_data(h5f,data,metadata):
    """
    

    Parameters
    ----------
    h5f : TYPE
        DESCRIPTION.
    data : TYPE
        DESCRIPTION.
    metadata : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    for group in data:
        if group.endswith('data'):
            h5data = data[group]
            data_type = str(h5data.dtype)
            path = group[:-4]
            image = h5f[path].create_dataset('data',(h5data.shape[0],h5data.shape[1]),data_type,h5data,compression="gzip")

def write_odim(outfile,data,attr):
    """
    

    Parameters
    ----------
    outfile : TYPE
        DESCRIPTION.
    data : TYPE
        DESCRIPTION.
    attr : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile), exist_ok=True)

    temp_file_path = os.path.dirname(outfile)

    with tempfile.NamedTemporaryFile(dir=temp_file_path) as temp_file:

        with h5py.File(temp_file.name, 'w') as h5f:
            groups = list(attr.keys())
            create_groups(h5f,groups)
            write_data(h5f,data,attr)
            write_attr(h5f,attr)

        # Rename the temp file to the outfile path and name if successful
        shutil.copy(temp_file.name, outfile)

  
    
    