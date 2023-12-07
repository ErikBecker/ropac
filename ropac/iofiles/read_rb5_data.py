#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 16:38:05 2023

@author: ebecker
"""

import wradlib as wrl

def read_file(fileName: str):
    
    volume = {}
    rb5data = wrl.io.read_rainbow(fileName)       
    volume[fileName] = rb5data['volume']
    
    return volume

def read_file_list(rb5files: list):
    
    volume = {} 
    for fileName in rb5files:
        rb5data = wrl.io.read_rainbow(fileName)
        volume[fileName] = rb5data['volume']
    
    return volume

if __name__ == '__main__':
    
    # rb5file = '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200dBZ.vol'
    # rb5file = '/home/ebecker/sf_data/archive/RB5/2021/Seletar/sel_240km_20161116_rs5.azi/2021-04-17/2021041704020500V.azi'
    
    rb5files = ['/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200dBuZ.vol',
                  '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200dBuZv.vol',
                  '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200dBZ.vol',
                  '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200dBZv.vol',
                  '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200KDP.vol',
                  '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200PhiDP.vol',
                  '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200RhoHV.vol',
                  '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200uPhiDP.vol',
                  '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200V.vol',
                  '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200W.vol',
                  '/home/ebecker/sf_data/archive/RB5/2021/Changi/NEAMSD_op.vol/2021-04-17/2021041704052200ZDR.vol']

    # rb5files = ['/home/ebecker/sf_data/archive/RB5/2021/Seletar/sel_240km_20161116_rs5.azi/2021-04-17/2021041704020500V.azi',
    #              '/home/ebecker/sf_data/archive/RB5/2021/Seletar/sel_240km_20161116_rs5.azi/2021-04-17/2021041704020500ZDR.azi',
    #              '/home/ebecker/sf_data/archive/RB5/2021/Seletar/sel_240km_20161116_rs5.azi/2021-04-17/2021041704020500dBZ.azi',
    #              '/home/ebecker/sf_data/archive/RB5/2021/Seletar/sel_240km_20161116_rs5.azi/2021-04-17/2021041704020500dBuZ.azi',
    #              '/home/ebecker/sf_data/archive/RB5/2021/Seletar/sel_240km_20161116_rs5.azi/2021-04-17/2021041704020500W.azi',
    #              '/home/ebecker/sf_data/archive/RB5/2021/Seletar/sel_240km_20161116_rs5.azi/2021-04-17/2021041704020500RhoHV.azi',
    #              '/home/ebecker/sf_data/archive/RB5/2021/Seletar/sel_240km_20161116_rs5.azi/2021-04-17/2021041704020500KDP.azi',
    #              '/home/ebecker/sf_data/archive/RB5/2021/Seletar/sel_240km_20161116_rs5.azi/2021-04-17/2021041704020500PhiDP.azi',
    #              '/home/ebecker/sf_data/archive/RB5/2021/Seletar/sel_240km_20161116_rs5.azi/2021-04-17/2021041704020500uPhiDP.azi']

    # dataset = read_file(rb5file)
    
    dataset = read_file_list(rb5files)
