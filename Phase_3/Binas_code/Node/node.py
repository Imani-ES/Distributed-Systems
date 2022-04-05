import socket
import time
import threading
import json
import traceback
import os

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
def lead(socket):
    print("Starting "+name+ " as leader")
    state = 'l'
    #set up sockets and stuff
    while True:
        #lead
        data, addr = socket.recvfrom(port)
        print("received message: %s"%data)

#set up follower functionality
def follow(socket):
    print("Starting "+name+ " as follower")

    #countdown for follower state
    print("Starting countdown thread")    
    t = timeout
    while t > 0:
        #kep reseting countdown when leader exists
        if leaderexists:
            t = timeout

        #if leader stops existing, end countdown
        else:
            t = 0
        t -= 1
        time.sleep(1)
    
    #switch to candidate state
    state = 'c'
    
    return 0


#handles all messages
def message_handle(msg,addr):
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
        print(f"{name} responding in a follower fashion")

    else:
        print(f"{name} responding in a dead node fashion")

    return response


if __name__ == "__main__":
    print(f"Starting "+ name)

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