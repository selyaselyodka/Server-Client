import socket
import numpy as np
import encodings
import time
import sys
import errno
import threading
import subprocess
import minimalmodbus
import usb.core

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


# ===============================
# Additional functions and logic (leave original loop untouched)
# ===============================

def read_sensor_registers(sensor):
    """
    Reads a full set of sensor registers. Adjust addresses as needed.
    """
    try:
        return {
            # Float values (32-bit, span 2 registers each)
            'temperature_celsius': sensor.read_float(257, functioncode=3),
            'humidity_percent': sensor.read_float(259, functioncode=3),

            # 16-bit integer values
            'control_mode': sensor.read_register(300, functioncode=3),
            'status_flag': sensor.read_register(301, functioncode=3),
            'error_code': sensor.read_register(302, functioncode=3),
            'raw_temp_adc': sensor.read_register(304, functioncode=3),
            'raw_humidity_adc': sensor.read_register(305, functioncode=3),
            'firmware_version': sensor.read_register(400, functioncode=3),
        }
    except Exception as e:
        print(f"[ERROR] Failed to read full register set: {e}")
        return {}

def start_purge(sensor):
    """
    Sends a command to begin purge/calibration by writing 1 to control register 300.
    """
    try:
        print("[INFO] Sending purge/calibration command...")
        sensor.write_register(300, 1, functioncode=16)
    except Exception as e:
        print(f"[ERROR] Could not write to control register: {e}")

def wait_for_completion(sensor):
    """
    Waits for the sensor to report calibration complete by checking status_flag.
    """
    print("[INFO] Waiting for purge/calibration to complete...")
    while True:
        try:
            status = sensor.read_register(301, functioncode=3)
            print(f"[DEBUG] Status = {status}")
            if status == 1:
                print("[✅ DONE] Purge/calibration finished.")
                break
        except Exception as e:
            print(f"[ERROR] Reading status register: {e}")
        time.sleep(1)

# === Optional: Trigger purge logic ===
# Uncomment this block to run a purge/calibration cycle

"""
# === Start purge or calibration ===
start_purge(sensor)

# === Wait until done ===
wait_for_completion(sensor)

# === Read full sensor register set ===
print("\n[INFO] Final sensor data after purge:")
full_data = read_sensor_registers(sensor)
for key, value in full_data.items():
    print(f"{key}: {value}")
"""
