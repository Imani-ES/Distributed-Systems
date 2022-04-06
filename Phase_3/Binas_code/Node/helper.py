import json
import socket
import time
import threading
import json
import traceback
import os

def send_message(msg,reciever,socket,port):
    try:
        # Encoding and sending the message
        socket.sendto(json.dumps(msg).encode('utf-8'), (reciever, port))
    except:
        #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
        print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")
    return 0

