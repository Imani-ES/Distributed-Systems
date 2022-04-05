import time
import socket
import json
import os

# Get environment variables
name = os.getenv('app_name')
port = os.getenv('Port')
uri = os.getenv('DB_connect')
db_name = os.getenv('db_name')
host = os.getenv('host')
network = os.getenv('rainbow_bridge')
lead = 0

#for followers to nominate them selves
def msg_nominate(sender):
    msg = {"msg": f"Hi, I am Node", "counter":counter}
    msg_bytes = json.dumps(msg).encode()
    return msg_bytes

#for followers to vote on other nominations
def msg_vote(sender,vote):
    msg = {"sender":name,"purpose":"vote","vote": vote}
    msg_bytes = json.dumps(msg).encode()
    UDP_Socket.sendto(msg_bytes, (targets[i], port))
    return 0

#for leaders to send messages to followers
def msg_heart_beat(counter):
    msg = {"msg": f"Hi, I am Node", "counter":counter}
    msg_bytes = json.dumps(msg).encode()
    return msg_byte


#set up leader functionality
def lead():
    print("Starting "+name+ " as leader")
    lead = 1
    #set up sockets and stuff
    while True:
        #lead
        data, addr = sock.recvfrom(port)
        print("received message: %s"%data)
    print(name+ " is now leading")
    return 0

#set up follower functionality
def follow():
    print("Starting "+name+ " as follower")
    #set up sockets and stuff
    print(name+ " is now following")
    return 0

if __name__ == "__main__":
    
    targets = ["Node2","Node3","Node4","Node5"]

    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((name, port))
    
    time.sleep(5)

    #nodes automatically follow at first
    follow()