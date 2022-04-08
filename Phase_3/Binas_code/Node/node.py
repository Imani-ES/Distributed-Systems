import socket
import time
import threading
import json
import traceback
import os
from helper import *
import random


# Get environment variables
name = os.getenv('app_name') 
port = int(os.getenv('Port'))
timeout = random.randint(10, 18)
#RAFT Variables
state = 'f' #can be either: f = follow; l = lead; c = candadite; d = dead
leaderexists = 0
log = {}
term = 0
termvotes=0
termcandidates = {}
voted = 0
# Read Message Templates
msg = json.load(open("Message.json"))


#set up leader functionality
def lead(socket) -> None:
    #set gloal variables
    global leaderexists, termcandidates, state, log, name, port, term, termvotes
    leaderexists = 1
    termvotes = 0
    termcandidates = {}
    term += 1

    print(name+ " is now a leader")
    
    msg_c = msg
    #send heartbeats every half second
    while state == 'l':
        # Build RequestVote RPC
        msg_c['sender_name'] = name
        msg_c['request'] = "HEARTBEAT"
        msg_c['term'] = term
        if len(log) > 0:
           msg_c['last_log'] = log[len(log)-1]
        msg_c['log_length'] = len(log)
        print(f"{name} created Append RPC: {msg}")
        #broadcast message
        send_message(msg_c,"",socket,port)
        time.sleep(.5)


#set up candidate functionality
def candidate(socket) -> None:
    #set gloal variables
    global leaderexists, timeout, state, log, name, port, term, termvotes

    print(name+ " is now a candidate")
    msg_c = msg

    # Build RequestVote RPC
    msg_c['sender_name'] = name
    msg_c['request'] = "VOTEME"
    msg_c['term'] = term
    if len(log) > 0:
        msg_c['last_log'] = log[len(log)-1]
    msg_c['log_length'] = len(log)
    print(f"{name} Going on campaign: {msg_c}")
    send_message(msg_c,"",socket,port)

    #wait some time for votes to come in
    time.sleep(5)

    #let other candidates know aboout votes
    print("Sending out concensus")
    msg_c['request'] = "VOTECONCENSUS"
    msg_c['votes'] = termvotes
    send_message(msg_c,"",socket,port)

    #wait some time for nodes to come to concensus
    while len(termcandidates) == 0:     
        print("waiting for concensus")
        time.sleep(.25)
    time.sleep(5)

    #add up votes
    print("Deciding leader")
    tie = 0
    for v in termcandidates:
        if termcandidates[v] > termvotes:#become follower
            state = 'f'
            leaderexists = 1
            tie = 0
            threading.Thread(target=follow, args=[socket]).start()
            return
        elif termcandidates[v] == termvotes:
            tie = 1
    
    if tie: #become follower
            state = 'f'
            leaderexists = 0
            threading.Thread(target=follow, args=[socket]).start()

    else:   #become leader
        term += 1
        state = 'l'
        threading.Thread(target=lead, args=[socket]).start()
    
    return


#set up follower functionality
def follow(socket) -> None:
    #set gloal variables
    global leaderexists, timeout, state, name, termvotes, msg, voted, termcandidates 
    t = timeout
    termvotes = 0
    termcandidates = {}
    print(name+ " is now a follower, Starting Countdown")

    #countdown for follower state
    while t > 0:
        print(f"{t} seconds left until I run for office")
        
        if leaderexists: #keep reseting countdown when leader exists
            t = timeout
            leaderexists = 0 #toggle leaderexists back
        
        else: #if leader stops existing, end countdown
            t = 0  
        
        t -= 1
        time.sleep(1)    
    
    #switch to candidate state
    print("Beginning insurrection")
    state = 'c'
    threading.Thread(target=candidate, args=[socket]).start()

#handles all messages
def message_handle(msg_in,addr,socket) -> None:
    #set gloal variables
    global leaderexists, timeout, state, log, name, port, term, termvotes, msg, voted
    msg_c = msg

    #Decodemessage
    dm = json.loads(msg_in.decode('utf-8'))
    print(f"{name} Received the following message:{addr} => {dm}, responding as a {state}")
    response = 0
    Request = dm['request']
    
    #node recieving command from controller
    if(dm['sender_name'] == "Controller"):
        #turn node into a follower
        if Request == 'FOLLOW':
            #change state to follower
            state = 'f'
        
        #turn node into a candidate
        if Request == 'TRYLEAD':
            if state != 'l':
                leaderexists = 0
        
        #have node play dead
        if Request == 'PLAYDEAD':
            state = 'd'
    
    #node recieving message from other node
    elif state != 'd':
        #follower recieving a candidate's vote request 
        if Request== "VOTEME":
            #if you havent voted yet, and the candadites logs are valid, give up your vote
            if voted == 0 and dm['term'] >= term and  dm['log_length']>=len(log):
                #vote yes
                msg_c['request'] = "LEADME"
                voted = 1
            else:
                #vote no
                msg_c['request'] = "!LEADME"
            #send out message
            msg_c['sender_name'] = name
            send_message(msg_c,dm["sender_name"],socket,port)

        #candidate recieving a follower's vote respopnse     
        elif Request == "LEADME":
            print(f"{dm['sender_name']} voted for me!!")
            termvotes += 1
        
        #candidate recieving a follower's vote respopnse  
        elif Request == "!LEADME":
            print(f"{dm['sender_name']} is a hater")
        
        #follower recieving a leader's heartbeat
        elif Request == "HEARTBEAT":
            #verify heartbeat
            if dm['term'] >= term and dm['log_length']>len(log):
                if state != 'f': #if node is a candidate or leader, but gets a valid Heartbeat,
                    state ='f'               
                    voted = 0
                leaderexists = 1
                term = dm['term']
                termvotes = 0
                #if heartbeat has a log, add it to follower's log
                if dm['last_log']:
                    log.add(dm['last_log'])
            else:#invalid heartbeat, follower will become candidate
                leaderexists = 0                

        #Candidates checking for new leader
        elif Request == "VOTECONCENSUS":
            termcandidates[dm['sender_name']] = dm['votes']
        
        #Bad Message
        else:
            print(f"Bad Message @{Request}")
    
    #node is dead
    else:
        print("Do Not Disturb")

    #update Controller
    msg_c['sender_name'] = name
    msg_c['request'] = "STATUS"
    msg_c['term'] = term
    if len(log) > 0:
        msg_c['last_log'] = log[len(log)-1]
    msg_c['log_length'] = len(log)
    msg_c['role'] = state
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