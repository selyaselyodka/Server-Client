import socket
import numpy as np
import encodings
import time
import sys
import errno
import threading

HOST = '192.168.4.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


def random_data():

    x1 = np.random.randint(0, 55, None)         # Dummy temperature
    y1 = np.random.randint(0, 45, None)         # Dummy humidigy
    my_sensor = "{},{}".format(x1,y1)
    return my_sensor                            # return data seperated by comma




def sender():
     try:
         print(f'Connection from {addr}')

         while True:
             my_data = random_data()
             x_encoded_data = my_data.encode('utf-8')
             conn.sendall(x_encoded_data)
             print(f'Sent: {my_data}')
             time.sleep(1)
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

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Server Started waiting for client to connect ")
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
        
    receiver_thread = threading.Thread(target=reciever,args=())
    sender_thread = threading.Thread(target=sender,args=())

    receiver_thread.start()
    sender_thread.start()

    sender_thread.join()
    receiver_thread.join()

