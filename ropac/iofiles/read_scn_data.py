import struct
import numpy as np

def read_file_header(fileContent: bytes):

    """_summary_

    Returns:
        _type_: _description_
    """

    header_size = 80
    header_byte_format = "<8Hh2Hh7H2h3Hlhlh10H"
    header = fileContent[:header_size]

    header_info = struct.unpack(header_byte_format,header)
    
    header_output = {
        'size_of_header': header_info[0],
        'format_version': header_info[1],
        'DPU_Log_time_year': header_info[2],
        'DPU_Log_time_month': header_info[3],
        'DPU_Log_time_day': header_info[4],
        'DPU_Log_time_hour': header_info[5],
        'DPU_Log_time_minute': header_info[6],
        'DPU_Log_time_second': header_info[7],
        'Latitude_degree': header_info[8],
        'Latitude_minute': header_info[9],
        'Latitude_second': header_info[10]/1000,
        'Longitude_degree': header_info[11],
        'Longitude_minute': header_info[12],
        'Longitude_second': header_info[13]/1000,
        'Antenna_Altitude_Upper': header_info[14],
        'Antenna_Altitude_Lower': header_info[15],
        'Antenna_rotation_speed_rpm': header_info[16]/10,
        'PRF1': header_info[17]/10,
        'PRF2': header_info[18]/10,
        'Noise_level_PM_H_dBm': header_info[19]/100,
        'Noise_level_FM_H_dBm': header_info[20]/100,
        'number_of_sweeps': header_info[21],  # sweep is a pulse ray in the context of the documentation.
        'number_of_range_bins': header_info[22],
        'range_resolution_m': header_info[23]/100,
        'radar_constant_mantissa_H': header_info[24],
        'radar_constant_characteristic_H': header_info[25],
        'radar_constant_mantissa_V': header_info[26],
        'radar_constant_characteristic_V': header_info[27],
        'Azimuth_Offset': header_info[28]/100,
        'UTC_time_year': header_info[29],
        'UTC_time_month': header_info[30],
        'UTC_time_day': header_info[31],
        'UTC_time_hour': header_info[32],
        'UTC_time_minute': header_info[33],
        'UTC_time_second': header_info[34],
        'Record_item': header_info[35],
        'Tx_pulse_blind_area_m': header_info[36],
        'Tx_pulse_specification': header_info[37]
        }

    header_output['Altitude_cm'] = header_output['Antenna_Altitude_Upper'] * 10000 + header_output['Antenna_Altitude_Lower']
    header_output['radar_constant_H'] = header_output['radar_constant_mantissa_H'] * pow(10,header_output['radar_constant_characteristic_H'])
    header_output['radar_constant_V'] = header_output['radar_constant_mantissa_V'] * pow(10,header_output['radar_constant_characteristic_V'])

    # # unpacking the bit string for the record item variable.
    # bstr = struct.pack("<H",header_output['Record_item'])
    # bytes_as_bits = ''.join(format(byte, '08b') for byte in bstr)

    return header_output

def read_ray_data(fileContent: bytes, header: dict):

    """_summary_

    Returns:
        _type_: _description_
    """
    
    data_byte_size = 9 * header['number_of_range_bins']
    data_byte_format = f'<3HH{data_byte_size}H'
    
    rays,ray_info = {},{}
    for i in range(header['number_of_sweeps']):
        ray = struct.unpack_from(data_byte_format, fileContent, offset=header['size_of_header'] + i * struct.calcsize(data_byte_format))
        #ray_info[i] = {'ray_ID_bytes':ray[0],'azimuth_start':ray[1]/100,'elevation':ray[2]/100,'ray_bytes':ray[3]}
        ray_info[i] = {'azimuth_start':ray[1]/100,'elevation':ray[2]/100}
        rays[i] = ray[4:]
        
    return {'info':ray_info,'data':rays}


def unpack_rays(rays: dict, header: dict):

    """_summary_

    Returns:
        _type_: _description_
    """
    
    moments = ['Rain','Zh','V','Zdr','Kdp','PhiDP','RhoHV','W','QI']
    
    scn_data = {}

    # Rain (Rainfall intensity)
    # Range: 0 - 65535
    # Calculation formula, N is a recording level.
    # Rain［mm/h]= (N-32768)/100
    # Rain Range: -327.67 - 327.67mm/h
    # Resolution: 0.01mm/h
    # N=0 is invalid
    
    # Zh (Reflective factor Horizontal polarization)
    # Range: 0 - 65535
    # Calculation formula, N is a recording level.
    # Zh［dBZ]= (N-32768)/100
    # Zh Range: -327.67 - 327.67dBZ
    # Resolution: 0.01dBZ
    # N=0 is invalid
    
    # V (Doppler velocity)
    # Range: 0 - 65535
    # Calculation formula, N is a recording level.
    # V［m/s]= (N-32768)/100
    # V Range: -327.67 - 327.67m/s
    # Resolution: 0.01m/s
    # N=0 is invalid
    
    # Zdr (Differential reflectivity)
    # Calculation formula, N is a recording level.
    # Zdr[dB]= (N-32768)/100
    # Zdr Range: -327.67 ~ 327.67dB
    # Resolution: 0.01dB
    # N=0 is invalid
    
    # Kdp (Specific differential phase)
    # Calculation formula, N is a recording level.
    # Kdp［deg/km]= (N-32768)/100
    # Kdp Range: -327.67 ~ 327.67deg/km
    # Resolution: 0.01deg/km
    # N=0 is invalid
    
    # Φdp (Differential phase)
    # Calculation formula, N is a recording level.
    # φdp[deg]=360x(N-32768)/65535
    # φdp Range: -179.9972 ~ 179.9972deg
    # Resolution: 0.0055deg
    # N=0 is invalid
    
    # ρhv (Correlation coefficient between Zh and Zv) *Corrected by S/N
    # Calculation formula, N is a recording level.
    # ρhv[no unit]=2 x (N-1)/65534
    # ρhv Range:0.0 ~ 2.0
    # Resolution: 0.0000030
    # N=0 is invalid
    
    # W (Doppler velocity width)
    # Range: 0 - 65535
    # Calculation formula, N is a recording level.
    # W[m/s]= (N-1)/100
    # W Range: 0.00 - 655.34m/s
    # Resolution: 0.01m/s
    # N=0 is invalid
    
    # QI (Quality information)
    # bit0: signal shielding
    # bit1: signal extinction
    # bit2: ground clutter reference
    # bit3-5: ground clutter intensity
    #     0: Less than 0.1mm/h
    #     1: 0.1mm/h or more
    #     2: 1.0mm/h or more
    #     3: 5.0mm/h or more
    #     4: 10.0mm/h or more
    #     5: 20.0mm/h or more
    #     6: 50.0mm/h or more
    #     7: 100.0mm/h or more
    # bit6: pulse blind area
    # bit7: sector blank
    # bit8: 1 fixed (bit3-7 show additional)
    # bit9-15: reserved
    # # # unpacking the bit string for QI.
    # # bstr = struct.pack("<H",QI)
    # # bytes_as_bits = ''.join(format(byte, '08b') for byte in bstr)
    
    #initialise
    for moment in moments:
        scn_data[moment] = np.ones((header['number_of_sweeps'],header['number_of_range_bins']),dtype=float) * -99.
        
    #fill 2D array rows and columns with ray values
    for i,ray in enumerate(rays['data']):
        for j,moment in enumerate(moments):
            istart = j * header['number_of_range_bins']
            iend = j * header['number_of_range_bins'] + header['number_of_range_bins'] 
            scn_data[moment][i,:] = rays['data'][i][istart:iend]
            
    #convert recorded to standard SI (see comments)
    for moment in moments:        
        if moment == "W":
            scn_data[moment] = (scn_data[moment] - 1) / 100
        elif moment == "RhoHV":
            scn_data[moment] = 2 * (scn_data[moment] - 1) / 65534
        elif moment == "PhiDP":
            scn_data[moment] = 360 * (scn_data[moment] - 32768) / 65535
        elif moment == "QI":
            scn_data[moment] = scn_data[moment]
        else:
            scn_data[moment] = (scn_data[moment] - 32768) / 100
            
    return scn_data


def read_scn_file(radar_number: str,timestamp: str, elevation_number: str, method: str,datadir: str):
    
    #  scn file name:
    #  Radar/Product  number [radar_number]:  xxxx
    #  Start Time [timestamp]: yyyymmdd_hhmmss UTC 
    #  Elevation [elevation_number]  n starting elevation -> an ending elevation with sequence number from 01.
    #  Modulation method: ** (00: Pulse modulation, 01: Frequency modulation (Pulse modulation), 02: 00+01(Alternate transmission)) 

    fileName = f'{datadir}/{radar_number}_{timestamp}_{elevation_number}_{method}.scn'

    with open(fileName, mode='rb') as file: 
        fileContent = file.read()

    header = read_file_header(fileContent)
    rays = read_ray_data(fileContent,header)
    scn = unpack_rays(rays, header)
    
    return {'header':header,'ray_info':rays['info'],'data':scn}

def read_scn_file_list(scnfiles: list):
    
    volume = {}
    
    for fileName in scnfiles:
    
        with open(fileName, mode='rb') as file: 
            fileContent = file.read()
    
        header = read_file_header(fileContent)
        rays = read_ray_data(fileContent,header)
        scn = unpack_rays(rays, header)
        
        volume[fileName] = {'header':header,'ray_info':rays['info'],'data':scn}
    
    return volume


if __name__ == '__main__':
    
    datadir = "../data"
    radar_number = '2014'
    timestamp = '20211118_010200'
    elevation_number = '01'
    method = '02'
    
    scn_data = read_scn_file(radar_number,timestamp,elevation_number,method,datadir)

    print(scn_data)

