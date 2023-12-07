
import os

from datetime import datetime, timedelta

import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MinuteLocator

from ropac import Moment
from ropac import Elevation

from ropac.iofiles.read_write_odim import write_odim
from ropac.iofiles.read_write_odim import read_odim

from ropac.config.polar_metadata import TopHow, TopWhat, TopWhere
from ropac import system_config as syscfg

from ropac.convert.rb52odim import convert_rb5
from ropac.convert.scn2odim import convert_scn

from ropac.utils.colours import get_colour_map
from ropac.utils.helpers import are_all_files, find_index_greater_than
from ropac.utils.logger import Logger

import wradlib

log = Logger(__file__, is_system=True)

class PolarVolume(object):

    def __init__(self, input_data = None):

        self.how = TopHow()
        self.what = TopWhat()
        self.where = TopWhere()

        if isinstance(input_data, str):

            # Check if it's a file
            if not os.path.isfile(input_data): raise ValueError("input_data variable is not a file.")
            
            # Check if it is a known file extension
            if input_data.endswith('.h5'):
                self.read_file(input_data)
            elif input_data.endswith('.scn'):
                self.convert_to_odim([input_data])
            elif input_data.endswith('.vol'):
                self.convert_to_odim([input_data])
            elif input_data.endswith('.azi'):
                self.convert_to_odim([input_data])
            else:
                raise ValueError("input_data variable is a file but with a unknown extension.")
                
        elif isinstance(input_data, list):      
            
            if are_all_files(input_data):     
                self.convert_to_odim(input_data)
            elif all(isinstance(item, Elevation) for item in input_data):
                self.dataset = input_data
            else:
                raise TypeError("Should be list(Elevation) or list(Files: str)")
                
        else:
            raise TypeError("Should be list(Moments) or Int")
        
    def convert_to_odim(self,filenames):
        
        if all(item.endswith('.scn') for item in filenames):
            rdata = convert_scn(filenames)
        elif all(item.endswith('.vol') for item in filenames):
            rdata = convert_rb5(filenames)
        elif all(item.endswith('.azi') for item in filenames):
            rdata = convert_rb5(filenames)
        else:
            raise ValueError("Files require all same extension.")

        self.dataset = rdata[0] 
        self.sort_odim_elevations()
        self.what = rdata[1] 
        self.where = rdata[2]  
        self.how = rdata[3] 
        
    def read_file(self,filename):
          
        data, attr = read_odim(filename)
    
        moment_data = {}
        for data_id in data:
            key = data_id.split('/')
            attr_id = data_id.split('/')
            attr_id[-1] = 'what'
            attr_id = '/'.join(attr_id)
    
            moment = Moment()
            moment.data = data[data_id]
            moment.what.load_attibute(attr[attr_id])
            if key[1] not in moment_data: 
                moment_data[key[1]] = [moment]
            else:
                moment_data[key[1]].append(moment)
    
        elevation_data = []
        for key,dataset in moment_data.items():
            elevation = Elevation()
            elevation.data = dataset
            elevation.how.load_attibute(attr[f'/{key}/how'])
            elevation.what.load_attibute(attr[f'/{key}/what'])
            elevation.where.load_attibute(attr[f'/{key}/where'])
            elevation_data.append(elevation)
            
        self.dataset = elevation_data
        self.sort_odim_elevations()
        self.where.load_attibute(attr['/where'])
        self.what.load_attibute(attr['/what'])
        self.how.load_attibute(attr['/how'])
          
    @property        
    def elevations(self):
        lst = []
        for dataset in self.dataset: 
            lst.append(dataset.elevation)
        return lst

    @property    
    def available_moments(self):
        lst = []
        for dataset in self.dataset:       
            lst.append(dataset.available_moments)
        return set([item for sublist in lst for item in sublist])

    @property    
    def starttimes(self):
        lst = []
        for dataset in self.dataset:
            lst.append(dataset.starttime)
        return lst

    @property    
    def endtimes(self):
        lst = []
        for dataset in self.dataset:
            lst.append(dataset.endtime)
        return lst

    @property    
    def scan_durations(self):
        lst = []
        for dataset in self.dataset:
            lst.append(dataset.scan_duration)
        return lst
    
    @property    
    def volume_time(self):
        dt = self.what.date + self.what.time
        return datetime.strptime(dt,"%Y%m%d%H%M%S")  

    @property
    def odim_object(self):
        return self.what.object
    
    def sort_odim_elevations(self):    
        # Find elevations sequence
        stime = self.starttimes
        tuples = [(value, index) for index, value in enumerate(stime)]
        sorted_tuples = sorted(tuples, key=lambda x: x[0])
        index_list = [sorted_tuple[1] for sorted_tuple in sorted_tuples]
        # sort elevations
        self.dataset = [self.dataset[i] for i in index_list]
        #fix scan_index
        for i,item in enumerate(self.dataset): item.how.scan_index = i + 1
        #fix what data time
        self.what.date = self.dataset[0].what.startdate
        self.what.time = self.dataset[0].what.starttime

    @property        
    def radar_ID(self):
        if "id=" in self.what.source:
            source = self.what.source.split(',')
            output_CMT = [x for x in source if 'CMT' in x]               
            item = output_CMT[0].split(':')[1]
            cmt_list = item.split(';')
            output_id = [x for x in cmt_list if x.split('=')[0]=="id"]
            radar_id = output_id[0].split("=")[1]
            return radar_id
        else:
            return None       
    
    @radar_ID.setter
    def radar_ID(self, value):
        source = self.what.source.split(',')
        if "CMT" in self.what.source:
            output_CMT = [x for x in source if 'CMT' in x]
            if output_CMT:
                item = output_CMT[0].split(':')[1]
                cmt_list = item.split(';')
                output_id = [x for x in cmt_list if x.split('=')[0] == "id"]
                if output_id:
                    # CMT and id are present, update the id
                    item = item.replace(f"id={output_id[0].split('=')[1]}", f"id={value}")
                else:
                    # CMT is present but no id, add the id
                    item += f";id={value}"
        else:
            # CMT is not present, add CMT:id
            source.append(f'CMT:id={value}')
        # Update the original source with the modified CMT section
        self.what.source = ','.join(source)
        

    @property        
    def radar_name(self):
        source = self.what.source.split(',')
        output_CMT = [x for x in source if 'PLC' in x]               
        item = output_CMT[0].split(':')[1]
        return item

    @property        
    def summary(self):
        summary = []
        summary.append(f"Radar: {self.what.source}")
        summary.append(f"Number of Elevations: {len(self.dataset)}")
        summary.append(f"Volume Time: {self.volume_time}")
        summary.append(f"Volume Start Time: {min(self.starttimes)}")
        summary.append(f"Volume End Time: {max(self.endtimes)}")
        summary.append(f"Available Moments: {self.available_moments}")
        summary.append(f"Elevation Angles: {self.elevations}")
        # summary.append(f"Scan Start Times: {self.get_starttimes()}")
        # summary.append(f"Scan End Times: {self.get_endtimes()}")
        # summary.append(f"Scan Duration: {self.scan_durations()}")
        return "\n".join(summary)
        
    @property
    def radar_site(self):
        return (self.where.lon,self.where.lat,self.where.height)
    
    def __str__(self):
        return self.summary
    
    def get_file_path(self,product=None,outdir=None):
        
        #"outdir"/"product"/"radar"/"data"/"file"
        
        if outdir==None:
            if product==None:
                outdir = os.path.join(syscfg.path.data)
            else:
                outdir = os.path.join(syscfg.path.data,product)
                
        filetime = self.volume_time
        
        filename = ".".join([str(self.radar_ID),filetime.strftime("%Y%m%d_%H%M%S"),self.odim_object.lower(),"h5"])
        filename = os.path.join(outdir,self.odim_object.lower(),str(self.radar_ID),filetime.strftime("%Y-%m-%d"),filename)
        
        return filename
    
    def return_scan(self,scan_index):
        for dataset in self.dataset:
            if dataset.scan_index == scan_index:
                return dataset
            
    def delete_quantity(self,quantity: str):
        for dataset in self.dataset:
            dataset.delete_quantity(quantity)
            
    def add_quantity(self, in_vol):
        
        if self.radar_site != in_vol.radar_site:
            log.error("Radar site do not match: {self.radar_site} != {in_vol.radar_site}")
            raise  ValueError("Radar site do not match")
        elif self.elevations != in_vol.elevations:
            log.error("Radar elevations do not match: {self.elevations} != {in_vol.elevations}")
            raise  ValueError("Radar elevations do not match")
        elif self.starttimes != in_vol.starttimes:
            log.error("Radar start times do not match: {self.starttimes} != {in_vol.starttimes}")
            raise  ValueError("Radar start times do not match")
        elif self.endtimes != in_vol.endtimes:
            log.error("Radar end times do not match: {self.endtimes} != {in_vol.endtimes}")
            raise  ValueError("Radar end times do not match")
        else:
            moments = [moment for moment in in_vol.available_moments if moment not in self.available_moments]
            log.debug(f"Adding the moments ({moments}) to PolarVolume")
            for i in range(len(self.dataset)):
                for moment in moments:
                    self.dataset[i].add_quantity(in_vol.dataset[i].return_quantity(moment))
                
            
                
    def write_to_file(self,product=None,outdir=None):
        
        filename = self.get_file_path(product=product,outdir=outdir)
        self.how.sys_time_created = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        log.info(f'Writing data to {filename}')
        
        h5attr = {'/':{'Conventions': 'ODIM_H5/V2_3'}}
        h5data = {}
        
        for var_name, value in vars(self).items():
            # print(var_name)
            if isinstance(value, list):
                for i, dataset in enumerate(value):
                    h5attr[f'/{var_name}{i+1}'] = {}
                    for dataset_name, dataset_value in vars(dataset).items():
                        
                        if isinstance(dataset_value, list):
                            for j, data in enumerate(dataset_value):
                                h5attr[f'/{var_name}{i+1}/{dataset_name}{j+1}'] = {}
                                for data_name, data_value in vars(data).items():
                                    if isinstance(data_value, np.ndarray):
                                        h5attr[f'/{var_name}{i+1}/{dataset_name}{j+1}/{data_name}'] = {'CLASS':'IMAGE','IMAGE_VERSION':'1.2'}
                                        h5data[f'/{var_name}{i+1}/{dataset_name}{j+1}/{data_name}'] = data_value
                                    if data_name!='data':                                        
                                        h5attr[f'/{var_name}{i+1}/{dataset_name}{j+1}/{data_name}'] = vars(data_value)
                        if dataset_name!='data':
                            h5attr[f'/{var_name}{i+1}/{dataset_name}'] = vars(dataset_value)
            if var_name!='dataset':
                # print(var_name,value)
                h5attr[f'/{var_name}'] = vars(value)
                
        write_odim(filename,h5data,h5attr)

    def write_stats(self):

        filename = os.path.basename(self.get_file_path())
        Radar = self.what.source.split(',')[0].split(':')[-1] 
        Object = self.odim_object
        created_time = self.how.time_created
        file_time = self.volume_time.strftime("%Y-%m-%d %H:%M:%S")        

        stats = get_pvol_stats(self.dataset,filename,Radar,Object,created_time,file_time)
        
        stats_file = os.path.join(syscfg.path.data,Object.lower(),f'{self.volume_time.strftime("%Y%m%d")}_{Object.lower()}.csv')
        
        for elev in stats:
            for moment in stats[elev]:
                write_stats_csv(stats[elev][moment],stats_file)

            
            
    def plot_scan_sequence(self):
        
        elevation = self.elevations
        stime = self.starttimes
        etime = self.endtimes
        
        start_time = stime[0].replace(second=0, microsecond=0)
        end_time = etime[-1].replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        time_array = np.arange(start_time, end_time, timedelta(seconds=1))
        total_time = int((time_array[-1] - time_array[0]).item().total_seconds())
        
        # Create a subplot
        fig, ax = plt.subplots()
        
        # Plot each value as a time series
        total_scan_time = 0
        for value, start_time, end_time in zip(elevation, stime, etime):
            mask = (time_array >= start_time) & (time_array <= end_time)
            ax.plot(time_array[mask], [value]*sum(mask), label=f"{value}")
            total_scan_time += sum(mask)
        
        # Set the x-axis limits
        ax.set_xlim(time_array[0], time_array[-1])

        # Set the x-axis tick labels to show only the hour and minute components
        date_formatter = DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(date_formatter)
        
        # Set the x-axis ticks to every minute
        minute_locator = MinuteLocator()
        ax.xaxis.set_major_locator(minute_locator)
        
        # Set the legend and labels
        ax.legend()
        ax.set_xlabel(f"Time ({start_time.strftime('%Y-%m-%d')})")
        ax.set_ylabel("Elevation (deg)")
        plt.title(f"{os.path.basename(self.get_file_path())} \n Total Scan time = {total_scan_time}s ({total_time}s)")
        
        # Show the plot
        plt.show()



    def __add__(self, other):
        
        if self.radar_site == other.radar_site:
            
            for dataset in other.dataset:
                if dataset.starttime not in self.starttimes and dataset.endtime not in self.endtimes:
                    self.dataset.append(dataset)
                elif dataset.starttime in self.starttimes and dataset.endtime in self.endtimes:
                    pass
                else:
                    raise ValueError("Overlap in scan times which is not physically possible")
                    
        else:
            raise ValueError("Radar Site mismatch: Locations of radar differ, cannot add elevations")