# Python libraries 
import socket                # Lets the Pi communicate over WiFi
import numpy as np          
import encodings             # Handles text encoding (also not used directly here)
import time                  # Used to pause the program for a few seconds
import sys                   # System-related operations (not used directly)
import errno                 # Error codes (useful for network errors)
import threading             # Allows multitasking (e.g., sending and receiving at the same time)
import subprocess            # Used to run system commands like rebooting the Pi
import minimalmodbus         # The main library used to talk to the Modbus sensor

import os.path               # Helps with working with files and folders
import csv                   # Helps write data into CSV files/spreadsheets


from datetime import datetime

# This funciton reads temperature and humidity from a Modbus sensor
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
    # Set up Modbus sensor connected to /dev/ttyUSB0 with slave address 240
    sensor = minimalmodbus.Instrument('/dev/ttyUSB0',240)	

    # Set the serial communication settings that match the sensor's expectations
    sensor.serial.baudrate = 9600				# BaudRate - how fast fata is sent
    sensor.serial.bytesize = 8					# Number of data bits to be requested
    sensor.serial.parity = minimalmodbus.serial.PARITY_NONE	# Parity Setting here is NONE but can be ODD or EVEN
    sensor.serial.stopbits = 2					# Number of stop bits
    sensor.serial.timeout  = 0.5					# Timeout time in seconds
    sensor.mode = minimalmodbus.MODE_RTU				# Mode to be used (RTU or ascii mode)

    # These improve stability by resetting the sensor buffer after each read
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

# THREAD THAT SENDS DATA TO LAPTOP/RECEIVER
def sender(conn, addr):
    """
    This function runs in a separate thread.
    It repeatedly sends the sensor data to the connected laptop over WiFi.
    """
    print(f"[INFO] Connected to {addr}")  # Show who connected
    try:
        while True:
            # Read the latest temperature and humidity from the sensor
            my_data = temperature_data(sensor)

            # Format the data as a readable string, e.g.:
            # "modbus_temp:23.45,modbus_humidity:55.20,"
            data_string = f"modbus_temp:{my_data['temperature']},modbus_humidity:{my_data['humidity']},"

            # Send the data to the client as a UTF-8 encoded message
            conn.sendall(data_string.encode('utf-8'))

            # Print what was sent (for debugging)
            print(f"[SENT] {data_string}")

            # Wait 1 second before sending again
            time.sleep(1)

    except (BrokenPipeError, ConnectionResetError):
        # If the client disconnects or crashes
        print("[ERROR] Connection lost.")
    finally:
        # Always close the connection if done
        conn.close()


# THREAD THAT RECEIVES COMMANDS FROM LAPTOP
def receiver(conn):
    """
    This function runs in a separate thread.
    It listens for messages from the laptop.
    If the message is 'quit', it tells the Raspberry Pi to reboot.
    """
    while True:
        try:
            # Receive up to 1024 bytes of data from the client
            data = conn.recv(1024).decode()

            # If client disconnects (no data), break the loop
            if not data:
                print("[INFO] Client disconnected.")
                break

            # If the message is 'quit', reboot the Raspberry Pi
            if data.strip().lower() == "quit":
                print("[INFO] Shutdown command received.")
                break

        except Exception:
            # Exit the loop if any error occurs while receiving
            break

    conn.close()

    # Run a Linux system command to reboot the Pi immediately
    subprocess.call(["shutdown", "-r", "now"])  # Use "-h" instead of "-r" to shut down instead of reboot


# START SOCKET SERVER (after sensor setup)

print("[START] Socket server launching...")

# Create a socket object using IPv4 and TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to IP address 192.168.4.1 and port 65432
# This IP should be the Pi’s address in hotspot mode (romps WiFi)
s.bind(('192.168.4.1', 65432))

# Allow only 1 incoming connection at a time
s.listen(1)

# Wait until a client (like your laptop) connects
conn, addr = s.accept()

# When a connection is made, start two threads:
# - One to send sensor data to the client
# - One to listen for 'quit' command from the client
sender_thread = threading.Thread(target=sender, args=(conn, addr))
receiver_thread = threading.Thread(target=receiver, args=(conn,))

# Start both threads (they run at the same time)
sender_thread.start()
receiver_thread.start()

# Wait until both threads finish before ending the program
sender_thread.join()
receiver_thread.join()

print("[EXIT] Server shut down.")

