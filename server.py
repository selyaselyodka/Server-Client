import socket
import numpy as np
import encodings
import time
import sys
import errno
import threading
import subprocess
import pyownet
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

#import multiprocessing
from oneWireTempReading import Thermometers


import os.path
import csv

from datetime import datetime

HOST = '192.168.4.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


def temperature_data():
    Sensors = Thermometers()
    allTemperatures = Sensors.readAllTemperatures()
    tempString = ""
    for key in allTemperatures:
        tempString+=str(key)+":"+str(allTemperatures[key])+","
    return tempString



def sender():
     try:
         print(f'Connection from {addr}')

        #initial_data = temperature_data()
        #initial_values = my_data.split(',')



        # writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        # writer.writeheader()
         while True:
             my_data = temperature_data()
             x_encoded_data = my_data.encode('utf-8')
             conn.sendall(x_encoded_data)
             print(f'Sent: {my_data}')
             values = my_data.split(',')
             values.pop()
             index=1
            # data_dict={}
            # for v in values:
                # key = 'temp '+str(index)
                 #data_dict[key] = v
                # index += 1

            # writer.writerows([data_dict])

     except IOError as e:
         if e.errno == errno.EPIPE:
                pass
     finally:
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

