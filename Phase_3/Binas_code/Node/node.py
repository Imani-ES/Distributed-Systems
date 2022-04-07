import socket
import time
import threading
import json
import traceback
import os
from helper import *

# Get environment variables
name = os.getenv('app_name') 
print(os.getenv('app_name'))
port = int(os.getenv('Port'))
timeout = int(os.getenv('timeout'))

#RAFT Variables
state = 'f' #can be either: f = follow; l = lead; c = candadite; d = dead
leaderexists = 0
log = {}
term = 0
termvotes=0

# Read Message Templates
msg = json.load(open("Message.json"))


#set up leader functionality
def lead(socket) -> None:
    #set gloal variables
    global leaderexists, timeout, state, log, name, port

    print(name+ " is now a leader")
    

#set up candidate dunctionality
def candidate(socket) -> None:
    #set gloal variables
    global leaderexists, timeout, state, log, name, port, term

    print(name+ " is now a candidate")
    msg_c = msg
    # Build RequestVote RPC
    msg_c['sender_name'] = name
    msg_c['request'] = "VOTEME"
    msg_c['term'] = term
    msg_c['last_log'] = log[len(log)-1]
    msg_c['log_length'] = len(log)
    print(f"{name} created Request Vote RPC: {msg}")

    #send message
    send_message(msg_c,"",socket,port)

    #wait some time for election
    time.sleep(10)
    if state == 'f':
        threading.Thread(target=follow, args=[socket]).start()
    if state == 'l':
        threading.Thread(target=lead, args=[socket]).start()
    


#set up follower functionality
def follow(socket) -> None:
    #set gloal variables
    global leaderexists, timeout, state, log, name, port    
    t = timeout

    print(name+ " is now a follower, Starting Countdown")

    #countdown for follower state
    while t > 0:
        print(f"{t} secoonds left until rebellion")
        if leaderexists: #keep reseting countdown when leader exists
            t = timeout
            leaderexists = 0 #toggle leaderexists back
        else: #if leader stops existing, end countdown
            t = 0  
            print("Beginning insurrection")
        t -= 1
        time.sleep(1)    
    #switch to candidate state
    state = 'c'
    threading.Thread(target=candidate, args=[socket]).start()
    time.sleep(5) #let the candidate thread start

#handles all messages
def message_handle(msg_in,addr,socket) -> None:
    #set gloal variables
    global leaderexists, timeout, state, log, name, port, term, termvotes
    msg_c = msg

    #Decodemessage
    dm = json.loads(msg_in.decode('utf-8'))
    print(f"{name} Received the following message:{addr} => {dm}, responding as a {state}")
    response = 0

    #respond to other nodes
    if state != 'd':
        #follower recieving a candidate's vote request 
        if dm['request'] == "VOTEME":
            if dm['term'] >= term and dm['last_log']>= len(log) and dm['log_length']>log[len(log)-1]['term']:
                #vote yes
                msg_c['sender_name'] = name
                msg_c['request'] = "LEADME"
                send_message(msg_c,dm["sender_name"],socket,port)
            else:
                #vote no
                msg_c['sender_name'] = name
                msg_c['request'] = "!LEADME"
                send_message(msg_c,dm["sender_name"],socket,port)

        #follower recieving a candidate's leader request 
        elif dm['request'] == 'FOLLOWME':
            if dm['term'] >= term and dm['last_log']>= len(log) and dm['log_length']>log[len(log)-1]['term']:
                #Follow them, increase term, start follower thread
                term += 1
                leaderexists = 1
                state = 'f'
                termvotes = 0

        #candidate recieving a follower vote respopnse     
        elif dm['request'] == "LEADME":
            print(f"{dm['sender_name']} voted for me!!")
            termvotes += 1
        #candidate recieving a follower vote respopnse  
        elif dm['request'] == "!LEADME":
            print(f"{dm['sender_name']} is a hater")
            termvotes -= 1
    
    #node recieving command from controller
    if(dm['sender_name'] == "Controller"):
        
    #update Controller
    
    msg_c['sender_name'] = name
    msg_c['request'] = "STATUS"
    msg_c['term'] = term
    msg_c['last_log'] = log[len(log)-1]
    msg_c['log_length'] = len(log)
    print(f"{name} created Request Vote RPC: {msg}")


if __name__ == "__main__":
    print(f"Starting "+ name)

    time.sleep(10) #Give controller some time to start up
    sender = name

    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((sender, 5555))

    #All nodes begin as followers
    threading.Thread(target=follow, args=[UDP_Socket]).start()

    #Main thread Listening at all times
    while True:
        mesg = 0
        try:
            mesg, addr = UDP_Socket.recvfrom(1024)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")

         #Messages are handled by creating threads
        if mesg:
            threading.Thread(target=message_handle, args=[mesg,addr,UDP_Socket]).start()

   

    #threading.Thread(target=listener, args=[UDP_Socket]).start()

    #Starting thread 2
    #threading.Thread(target=function_to_demonstrate_multithreading).start()

    #print("Started both functions, Sleeping on the main thread for 10 seconds now")
    #time.sleep(10)
    #print(f"Completed Node Main Thread Node 2")