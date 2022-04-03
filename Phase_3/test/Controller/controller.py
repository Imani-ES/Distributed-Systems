import json
import socket
import traceback
import time
import os


# Read Message Template
msg = json.load(open("Message.json"))

# Get environment variables
name = os.getenv('app_name')
port = os.getenv('Port')
network = os.getenv('rainbow_bridge')

# Initialize
sender = "Controller"
target = "Node_1"

# Request
msg['sender_name'] = sender
msg['request'] = "CONVERT_FOLLOWER"
print(f"Request Created : {msg}")

# Socket Creation and Binding
skt = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
skt.bind((sender, port))

# Wait following seconds below sending the controller request
time.sleep(5)

# Send Message
try:
    # Encoding and sending the message
    skt.sendto(json.dumps(msg).encode('utf-8'), (target, port))
except:
    #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
    print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")

