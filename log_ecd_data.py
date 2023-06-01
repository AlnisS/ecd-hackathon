import argparse
import time

import serial
from serial import Serial

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

ser = serial.Serial('/dev/cu.usbmodem14301',115200, timeout = 0.1, write_timeout = 0.1)

keep_running = True

while keep_running:
  try:
    message_flag = False
    line = ''
    while ser.in_waiting > 0:
      line = ser.readline().decode('UTF-8')
      message_flag = True
    if message_flag == True:
      print(line, end='')
      if write_to_file:
        output_file.write(line)
      backup_output_file.write(line)
      message_flag = False
  except KeyboardInterrupt:
    keep_running = False

print()

if write_to_file:
  output_file.close()
  print(f'output saved to {filepath}')

backup_output_file.close()
print(f'backup saved to {backup_filepath}')