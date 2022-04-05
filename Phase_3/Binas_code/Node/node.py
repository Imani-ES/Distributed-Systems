import socket
import time
import threading
import json
import traceback
import os

# Get environment variables
name = os.getenv('app_name') or "Node_1"
print(os.getenv('app_name'))
port = int(os.getenv('Port')) #or 8080
uri = os.getenv('DB_connect')
db_name = os.getenv('db_name')
host = os.getenv('host')
network = int(os.getenv('rainbow_bridge')) or 8080
lead = 0


#set up leader functionality
def lead(socket):
    print("Starting "+name+ " as leader")
    lead = 1
    #set up sockets and stuff
    while True:
        #lead
        data, addr = socket.recvfrom(port)
        print("received message: %s"%data)

#set up follower functionality
def follow(socket):
    print("Starting "+name+ " as follower")
    
    #while True:
    #    data, addr = socket.recvfrom(port)
    #    print("received message: %s"%data)
    return 0


# Listener
def listener(skt):
    print(f"Starting Listener ")
    while True:
        try:
            msg, addr = skt.recvfrom(1024)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")

        # Decoding the Message received from Node 1
        decoded_msg = json.loads(msg.decode('utf-8'))
        print(f"Message Received : {decoded_msg} From : {addr}")

        if decoded_msg['counter'] >= 4:
            break

    print("Exiting Listener Function")

# Dummy Function
def function_to_demonstrate_multithreading():
    for i in range(5):
        print(f"Hi Executing Dummy function : {i}")
        time.sleep(2)


if __name__ == "__main__":
    print(f"Starting Node 2")

    sender = "Node2"

    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((sender, 5555))

    #Starting thread 1
    threading.Thread(target=listener, args=[UDP_Socket]).start()

    #Starting thread 2
    threading.Thread(target=function_to_demonstrate_multithreading).start()

    print("Started both functions, Sleeping on the main thread for 10 seconds now")
    time.sleep(10)
    print(f"Completed Node Main Thread Node 2")