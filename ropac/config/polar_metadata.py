#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 03:50:29 2023

@author: ebecker
"""

from dataclasses import dataclass

@dataclass
class TopWhat:
    """
    object string - According to Table 2
    version string H5rad M.m Format or information model version. “M” is the major version. “m” is the minor version. Software is encouraged to warn if it receives a file stored in a version which is different from the one it expects. The software should, however, proceed to read the file,ignoring Attributes it does not understand.
    date string YYYYMMDD Nominal Year, Month, and Day of the data/product
    time string HHmmss Nominal Hour, Minute, and Second, in UTC of the data/product
    source string TYP:VALUE Variable-length string containing pairs of identifier types and their values, separated by a colon. Several pairs can be concatenated, separated by commas, in the form TYP:VALUE,TYP:VALUE, etc. At least one identifier according to Table 3 must be specified. All identifiers assigned to a given radar shall be provided
    """
    object: str = None
    version: str = 'H5rad 2.3'
    date: str = None
    time: str = None
    source: str = None
    
    def add_attribute(self, key, value):
        setattr(self, key, value)
        
    def load_attibute(self, attributes: dict):
        for key, value in attributes.items():
            self.add_attribute(key, value)

@dataclass
class TopWhere:
    """
    lon (double) # Longitude position of the radar antenna (degrees), normalized to the WGS-84 reference ellipsoid and datum. Fractions of a degree are given in decimal notation.
    lat (double) # Latitude position of the radar antenna (degrees), normalized to the WGS-84 reference ellipsoid and datum. Fractions of a degree are given in dec-imal notation.
    height (double) # Height of the centre of the antenna in meters above mean sea level.
    """
    height: float = None
    lat: float = None
    lon: float = None 
    
    def add_attribute(self, key, value):
        setattr(self, key, value)
        
    def load_attibute(self, attributes: dict):
        for key, value in attributes.items():
            self.add_attribute(key, value)

@dataclass
class TopHow:
    """
    Data from individual radars:
    beamwidth double The radar’s half-power beamwidth (degrees)
    beamwH double Horizontal half-power (-3 dB) beamwidth in degrees
    beamwV double Vertical half-power (-3 dB) beamwidth in degrees
    wavelength double Wavelength in cm
    RXbandwidth double Bandwidth in MHz that the receiver is set to when operating the radar with the above mentioned pulsewidth
    RXlossH double Total loss in dB in the receiving chain for horizontally-polarized signals, defined as the losses that occur between the antenna reference point and the receiver, inclusive.
    RXlossV double Total loss in dB in the receiving chain for vertically-polarized signals, defined as the losses that occur between the antenna reference point and the receiver, inclusive.
    antgainH double Antenna gain in dB for horizontally-polarized signals
    antgainV double Antenna gain in dB for vertically-polarized signals
    radconstH double Radar constant in dB for the horizontal channel. For the precise definition, see Appendix A
    radconstV double Radar constant in dB for the vertical channel. For the precise definition, see Appendix A
    NI double Unambiguous velocity (Nyquist) interval in ±m/s

    Polar data:
    scan_index long Which scan this is in the temporal sequence (starting with 1) of the total number of scans comprising the volume. 
    scan_count long The total number of scans comprising the volume. 
    astart double Azimuthal offset in degrees (◦) from 0◦ of the start of the first ray in the sweep. This value is positive where the gate starts clockwise after 0◦, and it will be negative if it starts before 0◦. In either case, the value must be no larger than half a ray’s width. 
    startazA (simple array of doubles) Azimuthal start angles (degrees) used for each gate in a scan. The number of values in this array corresponds with the value of where/nrays for that dataset.
    stopazA (simple array of doubles) Azimuthal stop angles (degrees) used for each gate in a scan. The number of values in this array corresponds with the value of where/nrays for that dataset

    Quality:
    NEZH double The total system noise expressed as the horizontally-polarized reflectivity (dBZ) it would represent at one km distance from the radar.
    NEZV double The total system noise expressed as the vertically-polarized reflectivity (dBZ) it would represent at one km distance from the radar.
    LOG double Security distance above mean noise level (dB) threshold value.

    General:
    system string According to Table 11
    TXtype string Transmitter type [magnetron; klystron; solid state]
    poltype string Polarization type of the radar [single; simultaneous-dual; switched-dual]
    polmode string Current polarity mode [LDR-H; single-H; LDR-V; single-V; simultaneous-dual; switched-dual]
    software string According to Table 12
    sw_version string Software version in string format, e.g. “5.1” or “8.11.6.2

    Data from individual radars:
    rpm double The antenna speed in revolutions per minute, positive for clockwise scanning, negative for counter-clockwise scanning. Marked for DEPRECATION.
    elevspeed double Antenna elevation speed (RHI mode) in degrees/s, positive values ascending, negative values descending. Marked for DEPRECATION.
    antspeed double Antenna speed in degrees/s (positive for clockwise and ascending, negative for counter-clockwise and descending
    pulsewidth double Pulsewidth in μs
  
    TXlossH double Total loss in dB in the transmission chain for horizontally-polarized signals, defined as the losses that occur between the calibration reference plane and the feed horn, inclusive.
    TXlossV double Total loss in dB in the transmission chain for vertically-polarized signals, defined as the losses that occur between the calibration reference plane and the feed horn, inclusive.
    injectlossH double Total loss in dB between the calibration reference plane and the test signal generator for horizontally-polarized signals.
    injectlossV double Total loss in dB between the calibration reference plane and the test signal generator for vertically-polarized signals.
    radomelossH double One-way dry radome loss in dB for horizontally-polarized signals
    radomelossV double One-way dry radome loss in dB for vertically-polarized signals
    gasattn double Gaseous specific attenuation in dB/km assumed by the radar processor (zero if no gaseous attenuation is assumed)
    nomTXpower double Nominal transmitted peak power in kW at the output of the transmitter (magnetron/klystron output flange)
    TXpower simple array of doubles Transmitted peak power in kW at the calibration reference plane. The values given are average powers over all transmitted pulses in each azimuth gate. The number of values in this array corresponds with the value of where/nrays for that dataset.
    powerdiff double Power difference between transmitted horizontally and vertically-polarized signals in dB at the the feed horn.
    phasediff double Phase difference in degrees between transmitted horizontally and vertically-polarized signals as determined from the first valid range bins
    Vsamples long Number of samples used for radial velocity measurements

    """
    beamwidth: float = None 
    wavelength: float = None 

    def add_attribute(self, key, value):
        setattr(self, key, value)
        
    def load_attibute(self, attributes: dict):
        for key, value in attributes.items():
            self.add_attribute(key, value)
        
@dataclass
class DatasetWhere:
    """
    Dataset specific
    elangle double Antenna elevation angle (degrees) above the horizon.
    nbins long Number of range bins in each ray
    rstart double The range (km) of the start of the first range bin
    rscale double The distance in meters between two successive range bins
    nrays long Number of azimuth or elevation gates (rays) in the object
    a1gate long Index of the first azimuth gate radiated in the scan
    # startaz double The azimuth angle of the start of the first gate in the sector (degrees)
    # stopaz double The azimuth angle of the end of the last gate in the sector (degrees)
    # startel double The elevation angle of the start of the first gate in the sector (degrees)
    # stopel double The elevation angle of the end of the last gate in the sector (degrees
    """
    elangle: float = None
    nbins: int = None
    rstart: float = None
    rscale: float = None
    nrays: int = None
    a1gate: int = None
    # startaz: float = None
    # stopaz: float = None
    # startel: float = None
    # stopel: float = None
    
    def add_attribute(self, key, value):
        setattr(self, key, value)
        
    def load_attibute(self, attributes: dict):
        for key, value in attributes.items():
            self.add_attribute(key, value)

@dataclass
class DatasetWhat:
    """
    product string - According to Table 15
    prodname string - Product name
    prodpar Tab. 16 - According to Table 16 for products. Only used for cartesian products.
    startdate string Starting YYYYMMDD Year, Month, and Day for the product
    starttime string Starting HHmmss Hour, Minute, and Second for the product
    enddate string Ending YYYYMMDD Year, Month, and Day for the product
    endtime string Ending HHmmss Hour, Minute, and Second for the product
    """
    product: str = None 
    # prodname: str = None
    startdate: str = None
    starttime: str = None
    enddate: str = None
    endtime: str = None
    
    def add_attribute(self, key, value):
        setattr(self, key, value)
        
    def load_attibute(self, attributes: dict):
        for key, value in attributes.items():
            self.add_attribute(key, value)

@dataclass
class DatasetHow:
    """
    lowprf double Low pulse repetition frequency in Hz
    midprf double Intermediate pulse repetition frequency in Hz
    highprf double High pulse repetition frequency in Hz
    """
    
    highprf: float = None
    lowprf: float = None
    CSR: float = None
    LOG: float = None
    SQI: float = None
    NEZH: float = None
    NEZV: float = None
    NI: float = None
    astart: float = None
    pulsewidth: float = None
    radconstH: float = None
    radconstV: float = None
    rpm: float = None
    scan_index: float = None
    startazA: float = None
    stopazA: float = None
    zdrcal: float = None
    
    def add_attribute(self, key, value):
        setattr(self, key, value)
        
    def load_attibute(self, attributes: dict):
        for key, value in attributes.items():
            self.add_attribute(key, value)
    
@dataclass
class DataWhat:
    """
    quantity string - According to Table 17
    gain double - Coefficient in quantity_value = offset + gain × raw_value used to convert to physical unit. Default value is 1.0.
    offset double - Coefficient in quantity_value = offset + gain × raw_value used to convert to physical unit. Default value is 0.0.
    nodata double - Raw value used to denote areas void of data (never radiated). Note that this Attribute is always a float even if the data in question is in another format.
    undetect double - Raw value used to denote areas below the measurement detection threshold (radiated but nothing detected). Note that this Attribute is always a float even if the data in question is in another format.
    """    
    quantity: str = None
    gain: float = None
    offset: float = None
    nodata: float = None
    undetect: float = None

    def add_attribute(self, key, value):
        setattr(self, key, value)
        
    def load_attibute(self, attributes: dict):
        for key, value in attributes.items():
            self.add_attribute(key, value)
            
        














# @dataclass
# class GeographicWhere:
#     """
#     projdef string The projection definition arguments, described above, which can be used with PROJ.4. See the PROJ.4 documentation for usage. Longi-    tude/Latitude coordinates are normalized to the WGS-84 ellipsoid and geodetic datum.
#     xsize long Number of pixels in the X dimension
#     ysize long Number of pixels in the Y dimension
#     zsize long Number of pixels in the Z dimension
#     zstart double Height in meters above mean sea level of the lowest pixel in the Z dimension
#     xscale double Pizel size in the X dimension, in projection-specific coordinates (often meters)
#     yscale double Pixel size in the Y dimension, in projection-specific coordinates (often meters)
#     zscale double Pixel size in the Z dimension (meters)
#     LL_lon double Longitude of the lower left corner of the lower left pixel
#     LL_lat double Latitude of the lower left corner of the lower left pixel
#     UL_lon double Longitude of the upper left corner of the upper left pixel
#     UL_lat double Latitude of the upper left corner of the upper left pixel
#     UR_lon double Longitude of the upper right corner of the upper right pixel
#     UR_lat double Latitude of the upper right corner of the upper right pixel
#     LR_lon double Longitude of the lower right corner of the lower right pixel
#     LR_lat double Latitude of the lower right corner of the lower right pixel
#     """
#     projdef: str
#     xsize: int
#     ysize: int
#     zsize: int
#     zstart: float
#     yscale: float
#     zscale: float
#     LL_lon: float
#     LL_lat: float
#     UL_lon: float
#     UL_lat: float
#     UR_lon: float
#     UR_lat: float
#     LR_lon: float
#     LR_lat: float
    