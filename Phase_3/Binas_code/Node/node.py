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
uri = os.getenv('DB_connect')
db_name = os.getenv('db_name')
host = os.getenv('host')
network = int(os.getenv('rainbow_bridge'))
lead = 0


#set up leader functionality
def lead(socket):
    print("Starting "+name+ " as leader")
    lead = 1
    #set up sockets and stuff
    while True:
        #lead
        data, addr = socket.recvfrom(port)
        print("received message: %s"%data)

#set up follower functionality
def follow(socket):
    print("Starting "+name+ " as follower")
    
    #while True:
    #    data, addr = socket.recvfrom(port)
    #    print("received message: %s"%data)
    return 0

#handles all messages
def message_handle(msg,addr):
    #Deco
    dm = json.loads(msg.decode('utf-8'))
    print(f"{name} Received the following message:{addr} => {dm}")
    
    if lead:
        print(f"{name} responding in a leader fashion")
    else:
        print(f"{name} responding in a follower fashion")

    return 0


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