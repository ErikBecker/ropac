
from datetime import datetime

from ropac.config.polar_metadata import DatasetWhat, DatasetWhere, DatasetHow
        
class Elevation(object):
    def __init__(self, input = None):
        
        self.data = []
        self.how = DatasetHow()
        self.what = DatasetWhat()              
        self.where = DatasetWhere()

    @property
    def elevation(self):
        return self.where.elangle
    
    @property
    def nbins(self):
        return self.where.nbins
    
    @property
    def nrays(self):
        return self.where.nrays
    
    @property
    def rscale(self):
        return self.where.rscale
    
    @property
    def rstart(self):
        return self.where.rstart
    
    @property
    def startazA(self):
        return self.how.startazA
    
    @property
    def stopazA(self):
        return self.how.stopazA
    
    @property
    def scan_index(self):
        return self.how.scan_index
    
    @property
    def NI(self):
        return self.how.NI
    
    @property    
    def starttime(self):
        dt = self.what.startdate + self.what.starttime
        return datetime.strptime(dt,"%Y%m%d%H%M%S")

    @property         
    def endtime(self):
        dt = self.what.enddate + self.what.endtime
        return datetime.strptime(dt,"%Y%m%d%H%M%S")  

    @property
    def scan_duration(self):
        return self.endtime - self.starttime

    @property    
    def available_moments(self):
        moment = []
        for data in self.data:
            moment.append(data.quantity)
        return moment
    
    def return_quantity(self,quantity):
        for data in self.data:
            if data.quantity == quantity:
                return data
    
    def delete_quantity(self,quantity):
        self.data = [data for data in self.data if data.quantity != quantity]

    def add_quantity(self,in_data):
        self.data.append(in_data)
    
    
    