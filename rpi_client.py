import socket
import threading
import time
import csv
from datetime import datetime
import os.path


HOST = '192.168.4.1'  # The server's hostname or IP address
PORT = 65432     # The port used by the server

 
def process_data_from_server(x):
    x1, y1 = x.split(",")
    return x1,y1

def reciever():
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            x_temperature,y_humidity = process_data_from_server(data)
            data_dict = [{'temp':x_temperature,'humidity':y_humidity}]
            writer.writerows(data_dict)

    finally:
         client_socket.close()

def sender():
    while True:
        message = input("Enter quit to stop")
        if(message.lower()=="quit"):
            client_socket.sendall(message.encode())
            break

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    dt = datetime.now().strftime("%d%m%Y%H%M%S")

    file_path = THIS_FOLDER+"/data/"+dt+".csv"
    csvfile = open(file_path, 'w+')
    fieldnames = ["temp","humidity"]
    writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
    writer.writeheader()

    receiver_thread = threading.Thread(target=reciever, args=())
    sender_thread = threading.Thread(target=sender, args=())

    receiver_thread.start()
    sender_thread.start()

    sender_thread.join()
    receiver_thread.join()

    print("Client connection closed.")

    