import socket
import numpy as np
import encodings
import time
import sys
import errno
import threading
import subprocess
import minimalmodbus


import os.path
import csv

from datetime import datetime


def temperature_data(sensor):
    temperature = sensor.read_register(257, functioncode=3)
    humidity = sensor.read_register(256, functioncode=3)
    temperature = temperature/100
    humidity = humidity/100
    return {
            'temperature': temperature,
            'humidity': humidity
        }

    #tempString = ""
    #for val in data:
        #tempString+=str(val)+","
    #return tempString

if __name__ == "__main__":
    sensor = minimalmodbus.Instrument('/dev/ttyUSB0',240)	
    sensor.serial.baudrate = 9600				# BaudRate
    sensor.serial.bytesize = 8					# Number of data bits to be requested
    sensor.serial.parity = minimalmodbus.serial.PARITY_NONE	# Parity Setting here is NONE but can be ODD or EVEN
    sensor.serial.stopbits = 2					# Number of stop bits
    sensor.serial.timeout  = 0.5					# Timeout time in seconds
    sensor.mode = minimalmodbus.MODE_RTU				# Mode to be used (RTU or ascii mode)


    sensor.clear_buffers_before_each_transaction = True
    sensor.close_port_after_each_call = True

    # writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
    # writer.writeheader()
    while True:
        my_data = temperature_data(sensor)
        print("Temperature "+str(my_data['temperature']))
        print("Humidity "+str(my_data['humidity']))
        time.sleep(1)
        #x_encoded_data = my_data.encode('utf-8')
        #conn.sendall(x_encoded_data)
        #print(f'Sent: {my_data}')
        #values = my_data.split(',')
        #values.pop()
    
    #THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    #file_path = THIS_FOLDER+"/data/"+dt+".csv"
    #csvfile = open(file_path, 'w+')


