import socket
import numpy as np
import encodings
import time
import sys
import errno
import threading
import subprocess
import minimalmodbus


#import multiprocessing
from oneWireTempReading import Thermometers


import os.path
import csv

from datetime import datetime

HOST = '192.168.4.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


def temperature_data(sensor):
    data =sensor.read_registers(0, 2, 3) 

    tempString = ""
    for val in data:
        tempString+=str(val)+","
    return tempString



def sender():
     try:
         print(f'Connection from {addr}')

        #initial_data = temperature_data()
        #initial_values = my_data.split(',')

         sensor = minimalmodbus.Instrument('/dev/ttyUSB0',240)	
         sensor.serial.baudrate = 9600				# BaudRate
         sensor.serial.bytesize = 8					# Number of data bits to be requested
         sensor.serial.parity = minimalmodbus.serial.PARITY_NONE	# Parity Setting here is NONE but can be ODD or EVEN
         sensor.serial.stopbits = 1					# Number of stop bits
         sensor.serial.timeout  = 0.5					# Timeout time in seconds
         sensor.mode = minimalmodbus.MODE_RTU				# Mode to be used (RTU or ascii mode)


         sensor.clear_buffers_before_each_transaction = True
         sensor.close_port_after_each_call = True

        # writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        # writer.writeheader()
         while True:
             my_data = temperature_data(sensor)
             x_encoded_data = my_data.encode('utf-8')
             conn.sendall(x_encoded_data)
             print(f'Sent: {my_data}')
             values = my_data.split(',')
             values.pop()

     except IOError as e:
         if e.errno == errno.EPIPE:
                pass
     finally:
         sensor.serial.close()
         conn.close()

def reciever():
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                print(f"Connection closed by client.")
                break
            if data.lower() == "quit":
                print(f"Client requeted to close the connection.")
                break
        except ConnectionAbortedError:
            print("Connection closed.")
            break
    conn.close()
    subprocess.call(["shutdown","-r","-t","0"])

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Server Started waiting for client to connect ")
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()

    dt = datetime.now().strftime("%d%m%Y%H%M%S")

    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    file_path = THIS_FOLDER+"/data/"+dt+".csv"
    csvfile = open(file_path, 'w+')


    receiver_thread = threading.Thread(target=reciever,args=())
    sender_thread = threading.Thread(target=sender,args=())

    receiver_thread.start()
    sender_thread.start()

    sender_thread.join()
    receiver_thread.join()

