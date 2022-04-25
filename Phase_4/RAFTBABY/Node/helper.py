import json
import socket
import time
import threading
import json
import traceback
import os

def send_message(msg,reciever,socket,port):
    #print(f"Sending {msg['request']} to {msg['recipient']} ")
    try:
        # Encoding and sending the message
        socket.sendto(json.dumps(msg).encode('utf-8'), (reciever, port))
    except:
        #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
        print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")
        return 1
    return 0

#node_info['log'][dm['prev_log_index']]['term'] <= dm['prev_log_term']
#@verify heartbeat:will this work if a node jumps in? (LaggingNode Needs to CATCHUP)

#bina's netindex would work, but it involves lots of overhead on the leader side
#might make more sense to have the LaggingNode give their latest 

#new node send out "Lagging" message,
#nodes respond with CATCHUP message and leader info
#leader sends CATCHUP message with logs
#Problem: When follower trying to catch up recieves heart beat, 
#   it cant accept the log since it's previous logs arent comparrable
#Solution: When followers get heart beat, instead of replying with "success = true or false,"
#   respond with the message index they are waiting for
#   The leader node will then reply based on that index
# Why not just have follower send CATCHUP, leader send entire log, 
# and let follower determine whole log?