import json
import socket
import time
import threading
import json
import traceback
import os

def send_message(msg,reciever,socket,port):
    print(f"Sending {msg['request']} to {msg['recipient']} ")
    try:
        # Encoding and sending the message
        socket.sendto(json.dumps(msg).encode('utf-8'), (reciever, port))
    except:
        #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
        print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")
        return 1
    return 0

#node_info['log'][dm['prev_log_index']]['term'] <= dm['prev_log_term']
#@verify heartbeat:will this work if a node jumps in?

#new node send out "CATCHUP" message,
#nodes respond with CATCHUP message and leader info
#leader sends CATCHUP message with logs