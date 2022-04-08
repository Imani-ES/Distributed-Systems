from email.mime import message
import json
import socket
import traceback
import time
import os
import threading
# Read Message Template
msg = json.load(open("Message.json"))

# Initialize
name = os.getenv('app_name') 
print(os.getenv('app_name'))
port = int(os.getenv('Port'))

# Socket Creation and Binding
skt = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
skt.bind((name, port))

def listener(socket,port) -> None:
    while True:
        try:
            mesg, addr = socket.recvfrom(1024)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")

         #Messages are handled by creating threads
        if mesg:
            threading.Thread(target=message_handle, args=[mesg,addr,socket]).start()

def message_handle(mesg,addr,socket) -> None:
    
    #Decodemessage
    dm = json.loads(mesg.decode('utf-8'))
    print(f"{name} Received the following message:{addr} => {dm}, responding as a {state}")
    

#start listening thread
threading.Thread(target=listener, args=[skt,port]).start()

#main thread taking commands
while True:
    print("Welcome to HQ, enter Node first, then it's role.")
    target= input("Enter an Node")
    req = input(f"Enter {target}'s new role: either [FOLLOW],[RUNFOROFFICE], or [DIE]")
     
    #Build message
    msg['sender_name'] = name
    msg['request'] = req

    # Request
    print(f"Request Created : {msg}")
    # Send Message
    try:
        # Encoding and sending the message
        skt.sendto(json.dumps(msg).encode('utf-8'), (target, port))
    except:
        #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
        print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")
    time.sleep(10)
