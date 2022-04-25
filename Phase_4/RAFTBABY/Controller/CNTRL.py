from email.mime import message
import json
import socket
import traceback
import struct
import time
import os
import threading
# Read Message Template
msg = json.load(open("Message.json"))

# Initialize
name = os.getenv('app_name') 
port = int(os.getenv('Port'))
group = os.getenv('group')



def message_handle(mesg) -> None:
    #Decodemessage
    dm = json.loads(mesg.decode('utf-8'))
    if dm['recipient'] == 'Controller':
        print(f"{name} Received the following message: {dm}")

def listener(socket) -> None:
    print ("Listening...")
    while True:
        try:
            mesg, addr = socket.recvfrom(1024)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")

         #Messages are handled by creating threads
         
        if mesg:
            threading.Thread(target=message_handle, args=[mesg]).start()


    

if __name__ == "__main__":
    print("Building socket")
    print("Building Multicast socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    time.sleep(25)
    #start listening thread
    threading.Thread(target=listener, args=[sock]).start()
    cycle = 0
    #main thread taking commands
    while True:
        #target= input("Enter an Node")
        #req = input(f"Enter {target}'s new role: either [FOLLOW],[RUNFOROFFICE], or [DIE]")
        #Build message
        if cycle%2:
            msg['sender_name'] = name
            msg['request'] = 'STORE'
            msg['key'] = 'Cycle'+str(cycle)
            msg['value'] = 'Chicken'
        elif cycle%3:        
            msg['sender_name'] = name
            msg['request'] = 'RETRIEVE'
        else:
            msg['sender_name'] = name
            msg['request'] = 'STATUS'
        
        # Request
        print(f"Sending Request: {msg}")
        # Send Message
        try:
            # Encoding and sending the message
            sock.sendto(json.dumps(msg).encode('utf-8'), (group, port))
        except:
            #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
            print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")
        cycle += 1
        time.sleep(10)
