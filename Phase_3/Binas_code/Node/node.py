import socket
import time
import threading
import json
import traceback
import os

print("hello world from the nodes")
# Get environment variables
name = os.getenv('app_name') 
print(os.getenv('app_name'))
port = int(os.getenv('Port'))
timeout = int(os.getenv('timeout'))

#RAFT Variables
state = 'f' #can be either: f = follow; l = lead; c = candadite; d = dead
leaderexists = 0
log = {}

#set up leader functionality
def lead(socket) -> None:
    #set gloal variables
    global leaderexists, timeout, state, log, name, port

    print(name+ " is now a leader")
    

#set up candidate dunctionality
def candidate(socket) -> None:
    #set gloal variables
    global leaderexists, timeout, state, log, name, port

    print(name+ " is now a candidate")

    #send out vote stuff
    
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
def message_handle(msg,addr):
    #set gloal variables
    global leaderexists, timeout, state, log, name, port

    #Decodemessage
    dm = json.loads(msg.decode('utf-8'))
    print(f"{name} Received the following message:{addr} => {dm}")
    response = 0
    #message processing
    if state == 'l':
        print(f"{name} responding in a leader fashion")

    elif state == 'c':
        print(f"{name} responding in a candidate fashion")

    elif state == 'f':
        leaderexists = 1 #signal heartbeat to follower
        print(f"{name} responding in a follower fashion")

    else:
        print(f"{name} responding in a dead node fashion")

    return response


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
        try:
            msg, addr = UDP_Socket.recvfrom(1024)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")

         #Messages are handled by creating threads
        if msg:
            threading.Thread(target=message_handle, args=[msg,addr]).start()

   

    #threading.Thread(target=listener, args=[UDP_Socket]).start()

    #Starting thread 2
    #threading.Thread(target=function_to_demonstrate_multithreading).start()

    #print("Started both functions, Sleeping on the main thread for 10 seconds now")
    #time.sleep(10)
    #print(f"Completed Node Main Thread Node 2")