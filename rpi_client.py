import socket
import threading
import time
import csv
from datetime import datetime
import os.path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


HOST = '192.168.4.1'  # The server's hostname or IP address
PORT = 65432     # The port used by the server

 
def process_data_from_server(x):
    x1, y1 = x.split(",")
    return x1,y1

def reciever():
    
    try:
        start_time = time.time()
        fig, ax = plt.subplots()
        x_data, y_data1, y_data2, y_data3 = [], [], [], []
        #line3, = ax.plot([], [], 'g-', label="Temp 3")
        first_data = client_socket.recv(1024).decode('utf-8')
        first_values = first_data.split(',')
        first_values.pop()
        fieldnames = []
        for v in first_values:
            pair = v.split(':')
            key = pair[0]
            fieldnames.append(key)

        fieldnames.append("Time")

        line1, = ax.plot([], [], 'b-', label=fieldnames[0])
        line2, = ax.plot([], [], 'r-', label=fieldnames[1])

        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()


        ax.set_title("Temperature Plot")
        ax.legend()

        def init():
            ax.set_ylim(0, 100)
            return line1, line2
        
        def update(frame):
            data = client_socket.recv(1024).decode('utf-8')
            current_time = time.time() - start_time
            #Temporary Measure
            #data = data.replace(',', '')

            values = data.split(',')
            values.pop()

            data_dict = {}
            for v in values:
                pair = v.split(':')
                key = pair[0]
                data_dict[key] = pair[1]
                data_dict["Time"] = str(datetime.now().hour)+':'+str(datetime.now().minute)+':'+str(datetime.now().second)
            
            #x_temperature,y_humidity = process_data_from_server(data)
            #data_dict = [{'temp':data}]

            writer.writerows([data_dict])
            x_data.append(current_time)
            y_data1.append(float(data_dict[fieldnames[0]]))
            y_data2.append(float(data_dict[fieldnames[1]]))
            #y_data3.append(float(data_dict['temp 3']))
            line1.set_data(x_data, y_data1)
            line2.set_data(x_data, y_data2)
            #line3.set_data(x_data, y_data3)
            ax.set_xlim(max(0, x_data[-1] - 10), x_data[-1] + 1) 
            #ax.set_ylim(min(min(y_data1), min(y_data2), min(y_data3)) - 1, max(max(y_data1), max(y_data2), max(y_data3)) + 1) 
            ax.set_ylim(min(min(y_data1), min(y_data2)) - 1, max(max(y_data1), max(y_data2)) + 1)    
            return line1, line2
        ani = FuncAnimation(fig, update, init_func=init, interval=1000, blit=False)
        plt.show()    
        
 

    finally:
        client_socket.close()
        quit_message = "quit"
        client_socket.sendall(quit_message.encode())

def sender():
    while True:
        message = input("Enter quit to stop\n")
        if(message.lower()=="quit"):
            client_socket.sendall(message.encode())
            client_socket.close()
            break

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    dt = datetime.now().strftime("%d%m%Y%H%M%S")

    file_path = THIS_FOLDER+"/data/"+dt+".csv"
    csvfile = open(file_path, 'w+')
    

    #receiver_thread = threading.Thread(target=reciever, args=())
    sender_thread = threading.Thread(target=sender, args=())

    #receiver_thread.start()
    sender_thread.start()

    reciever()

    sender_thread.join()
    #receiver_thread.join()

    print("Client connection closed.")

    