# === Required libraries ===
import socket                 # Used for WiFi communication (sending/receiving data between devices)
import numpy as np            # Math library (not used here, but commonly imported)
import encodings              # Handles text encoding (not used directly)
import time                   # Used for delays between readings
import sys                    # System-related tools (not used directly here)
import errno                  # Helps handle network errors
import threading              # Allows running multiple things at once (like sending and receiving data)
import subprocess             # Allows running system commands, like rebooting the Raspberry Pi
import minimalmodbus          # Library to talk to Modbus sensors over serial communication
import usb.core               # For accessing USB devices (not used directly here)

import os.path                # Helps manage file paths
import csv                    # Lets us save data to a spreadsheet if needed
from datetime import datetime # Used for timestamps (like logging when data is recorded)

# === Function to read temperature and humidity from the sensor ===
def temperature_data(sensor):
    # Read temperature and humidity registers from the Modbus sensor
    temperature = sensor.read_register(257, functioncode=3)
    humidity = sensor.read_register(256, functioncode=3)

    # The sensor gives values scaled by 100, so we divide to get actual values
    temperature = temperature / 100
    humidity = humidity / 100

    # Return the results as a dictionary (like a labeled container of values)
    return {
        'temperature': temperature,
        'humidity': humidity
    }

    # (Below is old code that returns a string instead of a dictionary — not used here)
    # tempString = ""
    # for val in data:
    #     tempString+=str(val)+","
    # return tempString

# === Main code starts here ===
if __name__ == "__main__":

    # Set up the Modbus sensor connected to the USB port (typically /dev/ttyUSB0)
    # Address 240 refers to the unique ID of the sensor on the Modbus network
    sensor = minimalmodbus.Instrument('/dev/ttyUSB0', 240)	

    # Configure the sensor communication settings
    sensor.serial.baudrate = 9600               # Speed of communication
    sensor.serial.bytesize = 8                  # Number of data bits
    sensor.serial.parity = minimalmodbus.serial.PARITY_NONE  # No parity check
    sensor.serial.stopbits = 2                  # Number of stop bits
    sensor.serial.timeout = 0.5                 # Time to wait for sensor to respond
    sensor.mode = minimalmodbus.MODE_RTU        # Use RTU (binary) Modbus protocol

    # These improve communication stability
    sensor.clear_buffers_before_each_transaction = True
    sensor.close_port_after_each_call = True

    # Repeatedly read data from the sensor and print to the terminal
    while True:
        my_data = temperature_data(sensor)
        print("Temperature " + str(my_data['temperature']))
        print("Humidity " + str(my_data['humidity']))
        time.sleep(1)

        # (The lines below are examples of sending or saving data — not used now)
        # x_encoded_data = my_data.encode('utf-8')
        # conn.sendall(x_encoded_data)
        # print(f'Sent: {my_data}')
        # values = my_data.split(',')
        # values.pop()

    # (The lines below are examples for saving to a CSV file — not used now)
    # THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    # file_path = THIS_FOLDER+"/data/"+dt+".csv"
    # csvfile = open(file_path, 'w+')


# ===============================
# 🧵 THREAD TO SEND DATA TO LAPTOP
# ===============================
def sender(conn, addr):
    """
    Sends the temperature and humidity readings from the Raspberry Pi to the laptop over WiFi.
    This runs in a separate thread (background task) so it doesn’t block anything else.
    """
    print(f"[INFO] Connected to {addr}")
    try:
        while True:
            my_data = temperature_data(sensor)  # Read data from sensor
            # Create a simple string like: "modbus_temp:23.5,modbus_humidity:45.0,"
            data_string = f"modbus_temp:{my_data['temperature']},modbus_humidity:{my_data['humidity']},"
            conn.sendall(data_string.encode('utf-8'))  # Send the data over WiFi
            print(f"[SENT] {data_string}")
            time.sleep(1)  # Wait one second before sending the next data
    except (BrokenPipeError, ConnectionResetError):
        print("[ERROR] Connection lost.")
    finally:
        conn.close()  # Close connection when done


# ===============================
# 📥 THREAD TO RECEIVE COMMANDS FROM LAPTOP
# ===============================
def receiver(conn):
    """
    Listens for commands sent by the laptop (e.g., the word 'quit').
    If 'quit' is received, the Raspberry Pi will reboot.
    """
    while True:
        try:
            data = conn.recv(1024).decode()  # Read up to 1024 bytes
            if not data:
                print("[INFO] Client disconnected.")
                break
            if data.strip().lower() == "quit":  # If the message is "quit"
                print("[INFO] Shutdown command received.")
                break
        except Exception:
            break
    conn.close()

    # Restart the Raspberry Pi (you can change "-r" to "-h" to power off instead)
    subprocess.call(["shutdown", "-r", "now"])


# ===============================
# 🌐 SETUP SOCKET SERVER
# ===============================
print("[START] Socket server launching...")

# Create a new socket using IPv4 and TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set up the socket to listen on IP address 192.168.4.1 and port 65432
# This works if the Raspberry Pi is acting as a WiFi hotspot (AP mode)
s.bind(('192.168.4.1', 65432))
s.listen(1)  # Allow 1 laptop to connect at a time

# Wait until a laptop connects
conn, addr = s.accept()

# Start the sender and receiver threads
# One sends sensor data to the laptop, the other listens for commands like 'quit'
sender_thread = threading.Thread(target=sender, args=(conn, addr))
receiver_thread = threading.Thread(target=receiver, args=(conn,))

# Start the background threads
sender_thread.start()
receiver_thread.start()

# Wait for both threads to finish before shutting down
sender_thread.join()
receiver_thread.join()

print("[EXIT] Server shut down.")
