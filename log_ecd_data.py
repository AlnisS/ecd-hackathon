import argparse
import time
import numpy as np

import serial
from serial import Serial

import ast

print('parsing arguments')

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-o', '--output', default='',
                        help='name of file to output to')
args = arg_parser.parse_args()

write_to_file = False

if len(args.output) > 0:
  write_to_file = True
  filepath = f'data/{args.output}'
  output_file = open(filepath, 'x')
  print(f'logging data to: {filepath}')

timestamp = int(time.time())
backup_filepath = f'data/backup/{timestamp}.txt'
backup_output_file = open(backup_filepath, 'x')
print(f'backup log file: {backup_filepath}')

# device_name = '/dev/cu.usbmodem14201'
device_name = '/dev/ttyACM0'
ser = serial.Serial(device_name, 115200, timeout = 0.1, write_timeout = 0.1)

keep_running = True

lut_temp = [-40,-39,-38,-37,-36,-35,-34,-33,-32,-31,-30,-29,-28,-27,-26,-25,-24,-23,-22,-21,-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200]
lut_R = [277.2,263.6,250.1,236.8,224,211.5,199.6,188.1,177.3,167,157.2,148.1,139.4,131.3,123.7,116.6,110,103.7,97.9,92.5,87.43,82.79,78.44,74.36,70.53,66.92,63.54,60.34,57.33,54.5,51.82,49.28,46.89,44.62,42.48,40.45,38.53,36.7,34.97,33.33,31.77,30.25,28.82,27.45,26.16,24.94,23.77,22.67,21.62,20.63,19.68,18.78,17.93,17.12,16.35,15.62,14.93,14.26,13.63,13.04,12.47,11.92,11.41,10.91,10.45,10,9.575,9.17,8.784,8.416,8.064,7.73,7.41,7.106,6.815,6.538,6.273,6.02,5.778,5.548,5.327,5.117,4.915,4.723,4.539,4.363,4.195,4.034,3.88,3.733,3.592,3.457,3.328,3.204,3.086,2.972,2.863,2.759,2.659,2.564,2.472,2.384,2.299,2.218,2.141,2.066,1.994,1.926,1.86,1.796,1.735,1.677,1.621,1.567,1.515,1.465,1.417,1.371,1.326,1.284,1.243,1.203,1.165,1.128,1.093,1.059,1.027,0.9955,0.9654,0.9363,0.9083,0.8812,0.855,0.8297,0.8052,0.7816,0.7587,0.7366,0.7152,0.6945,0.6744,0.6558,0.6376,0.6199,0.6026,0.5858,0.5694,0.5535,0.538,0.5229,0.5083,0.4941,0.4803,0.4669,0.4539,0.4412,0.429,0.4171,0.4055,0.3944,0.3835,0.373,0.3628,0.353,0.3434,0.3341,0.3253,0.3167,0.3083,0.3002,0.2924,0.2848,0.2774,0.2702,0.2633,0.2565,0.25,0.2437,0.2375,0.2316,0.2258,0.2202,0.2148,0.2095,0.2044,0.1994,0.1946,0.19,0.1855,0.1811,0.1769,0.1728,0.1688,0.165,0.1612,0.1576,0.1541,0.1507,0.1474,0.1441,0.141,0.1379,0.135,0.1321,0.1293,0.1265,0.1239,0.1213,0.1187,0.1163,0.1139,0.1115,0.1092,0.107,0.1048,0.1027,0.1006,0.0986,0.0966,0.0947,0.0928,0.0909,0.0891,0.0873,0.0856,0.0839,0.0822,0.0806,0.079,0.0774,0.0759,0.0743,0.0729,0.0714,0.07,0.0686,0.0672,0.0658,0.0645,0.0631,0.0619]
lut_temp.reverse()
lut_R.reverse()

def get_lut_temp(R):
  return np.interp(R, lut_R, lut_temp)

def v_raw_to_volts(v_raw):
  return v_raw * 3.3 / 65536

# sensed voltage (V) to thermistor resistance (kOhm)
def sense_V_to_thermistor_R(volts):
  thermistor_V = volts
  sense_V = 3.3 - thermistor_V
  sense_I = sense_V / 10000 # current through 10k resistor
  thermistor_R = thermistor_V / sense_I
  return thermistor_R / 1000

lines_read = 0

while keep_running:
  time.sleep(0.001)  # prevent spinning through really fast
  try:
    message_flag = False
    line = ''
    while ser.in_waiting > 0:
      line = ser.readline().decode('UTF-8')
      lines_read += 1
      if lines_read > 2: # first line is junk
        message_flag = True
    if message_flag == True:
      backup_output_file.write(line)
      # print(line, end='')
      # print(line)
      data = ast.literal_eval(line)
      csvline = ','.join(str(f) for f in data)

      sample_time_start = data[0]
      sample_time_end = data[1]
      a0_V = data[2]
      a1_V = data[3]
      a2_V = data[4]
      a3_V = data[5]

      pressure_sense_R = 49.9  # ohms
      a0_I = a0_V / pressure_sense_R * 1000.0  # milliamps
      a1_I = a1_V / pressure_sense_R * 1000.0  # milliamps
      a0_pressure = (a0_I - 4.0) * 1000.0 / 16.0
      a1_pressure = (a1_I - 4.0) * 1000.0 / 16.0
      
      a2_R = sense_V_to_thermistor_R(a2_V)
      a3_R = sense_V_to_thermistor_R(a3_V)
      a2_temperature = get_lut_temp(a2_R)
      a3_temperature = get_lut_temp(a3_R)

      # print(a0_pressure)
      # print(a1_pressure)
      # print(a2_V)
      # print(a3_V)
      # print(a2_temperature)
      # print(a3_temperature)

      # print(f'{a0_pressure:6.1f},{a1_pressure:6.1f},{a2_temperature:4.2f},{a3_temperature:4.2f}')
      csvline = f'{sample_time_start}, {a0_pressure:6.2f}, {a1_pressure:6.2f}, {a2_temperature:5.2f}, {a3_temperature:5.2f}\n'
      print(csvline, end='')



    #   sample_time = data[0]
    #   current = data[1]
    #   v1_raw = data[2]
    #   v2_raw = data[3]
    #   v3_raw = data[4]
    #   v4_raw = data[5]

    #   pressure = (current - 4.0) * 1000.0 / 16.0
    #   v1_volts = v_raw_to_volts(v1_raw)
    #   v2_volts = v_raw_to_volts(v2_raw)
    #   v3_volts = v_raw_to_volts(v3_raw)
    #   v4_volts = v_raw_to_volts(v4_raw)

    #   t1_R = sense_V_to_thermistor_R(v1_volts)
    #   t2_R = sense_V_to_thermistor_R(v2_volts)
    #   t3_R = sense_V_to_thermistor_R(v3_volts)
    #   t4_R = sense_V_to_thermistor_R(v4_volts)
    #   # print(v1_volts)
    #   print(f'{t1_R:10.5f} {t2_R:10.5f} {t3_R:10.5f} {t4_R:10.5f} {current:5.1f}')
    #   t1_C = get_lut_temp(t1_R)
    #   t2_C = get_lut_temp(t2_R)
    #   t3_C = get_lut_temp(t3_R)
    #   t4_C = get_lut_temp(t4_R)
    #   # print(v1_volts, t1_R, t1_C)
    #   # print(f'{t1_C:10.5f} {t2_C:10.5f} {t3_C:10.5f} {t4_C:10.5f}')

      # print(csvline)
      if write_to_file:
        output_file.write(csvline)
      message_flag = False
  except KeyboardInterrupt:
    keep_running = False
  # except Exception as e:
  #   print(f'error, but continuing: {e}')
    

print()

if write_to_file:
  output_file.close()
  print(f'output saved to {filepath}')

backup_output_file.close()
print(f'backup saved to {backup_filepath}')