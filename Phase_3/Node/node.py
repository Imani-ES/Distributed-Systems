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

def create_msg(counter):
    msg = {"msg": f"Hi, I am Node", "counter":counter}
    msg_bytes = json.dumps(msg).encode()
    return msg_bytes


if __name__ == "__main__":

    print("Starting Node 1")
    time.sleep(5)

    sender = "Node1"
    target = "Node2"

    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((sender, 5555))

    # Sending 5 messages to Node 2
    for i in range(5):
        node1_msg_bytes = create_msg(i)
        UDP_Socket.sendto(node1_msg_bytes, (target, 5555))
        time.sleep(1)

    print("All messages were sent")
    print("Ending Node 1")
