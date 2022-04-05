print("Hello World from Nodes")
import time
import socket
import json
import os

# Read Message Template
msg = {
    "sender_name": None,
    "request": None,
    "term": None,
    "key": None,
    "value": None
  }
  

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

print("Hello World, "+name+ " is here trying to bond to port "+str(port))


# Creating Socket and binding it to the target container IP and port
UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind the node to sender ip and port
UDP_Socket.bind((name, port))

time.sleep(5)

#nodes automatically follow at first
follow(UDP_Socket)