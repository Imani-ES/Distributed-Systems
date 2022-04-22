import socket
import time
import threading
import json
from tokenize import group
import traceback
import os
from helper import *
import random
import struct
from webserver import *

# Get environment variables
name = os.getenv('app_name') 
port = os.getenv('Port') or 5555
group = os.getenv('group')
tor1 = os.getenv("tor_1")
tor2 = os.getenv("tor_2")
heartrate = os.getenv("heartrate")
client_host = os.getenv("client_host")
client_port = os.getenv("client_port")
#RAFT Variables
leaderexists = 0
termvotes=0
termcandidates = {}
current_leader = ''
find_leader = []
# Read Message Templates
msg = json.load(open("Message.json"))

#node info
node_info = {
    'term': 0,
    'votedFor': '',
    'state': 'f',
    'log':[{'term':0,'key':None,'value':None}], # Logs stored as [term, key, Value]
    'timeout':random.randint(tor1, tor2),
    'heartbeat_interval':heartrate
}

def lead(socket) -> None:
    #set gloal variables
    global leaderexists, termcandidates, group, node_info, name, port, termvotes
    msg_c = msg
    leaderexists = 1
    termvotes = 0
    termcandidates = {}
    heartbeat = node_info['heartbeat_interval'] 
    print(name+ " is now a leader")
    
    # run client application 
    run_client(client_host,client_port)

    while node_info['state'] == 'l':
        #send heartbeats
        msg_c['sender_name'] = name
        msg_c['request'] = 'HEARTBEAT'
        msg_c['recipient'] = 'E'
        msg_c['term'] = node_info['term']
        msg_c['prev_log_term'] = node_info['log'][len(node_info['log'])-1]['term']
        msg_c['prev_log_term'] = len(node_info['log'])-1
        msg_c['commit_index'] = len(node_info['log'])
        msg_c['entry'] = None
        send_message(msg_c,group,socket,port)
        time.sleep(heartbeat)
    
    # kill client application
    kill_client()
    

#set up candidate functionality
def candidate(socket) -> None:
    #set gloal variables
    global leaderexists,node_info, group, name, port, termvotes
    node_info['term'] += 1
    print(f"{name} is now a candidate for office. Going on campaign...")
    msg_c = msg

    # Build RequestVote RPC, send to erbody
    msg_c['sender_name'] = name
    msg_c['recipient'] = 'E'
    msg_c['request'] = "VOTEME"
    msg_c['term'] = node_info['term']
    msg_c['prev_log_term'] = node_info['log'][len(node_info['log'])-1]['term']
    msg_c['prev_log_index'] = len(node_info['log'])-1
    send_message(msg_c,group,socket,port)

    #wait some time for votes to come in
    time.sleep(3*node_info['timeout'])
    if node_info['state'] == 'f': # if recieved a valid heartbeat, switch to follow state
        threading.Thread(target=follow, args=[socket]).start()
        return
    
    #let other candidates know aboout votes
    msg_c['sender_name'] = name
    msg_c['request'] = "VOTECONCENSUS"
    msg_c['recipient'] = 'E'
    msg_c['key'] = 'votes'
    msg_c['value'] = termvotes
    send_message(msg_c,group,socket,port)
    
    print("waiting for concensus")
    while len(termcandidates) == 0:             
        time.sleep(node_info['timeout'])

    print("Deciding leader")
    tie = 0
    for v in termcandidates:#count votes
        if termcandidates[v] > termvotes:#become follower
            node_info['state'] = 'f'
            leaderexists = 1
            tie = 0
            threading.Thread(target=follow, args=[socket]).start()
            return
        elif termcandidates[v] == termvotes:#tie
            tie = 1
    
    if tie: #become follower
            node_info['state'] = 'f'
            leaderexists = 0
            threading.Thread(target=follow, args=[socket]).start()

    else:   #become leader
        node_info['state'] = 'l'
        threading.Thread(target=lead, args=[socket]).start()
    
    return

#set up follower functionality
def follow(socket) -> None:
    #set gloal variables
    global leaderexists, node_info, name, termvotes, msg, termcandidates 
    t = node_info['timeout']
    termvotes = 0
    termcandidates = {}
    print(name+ " is now a follower, Starting Countdown")
    time.sleep(5) # give leader a second
    #countdown for follower state
    while t > 0:    
        if leaderexists: #keep reseting countdown when leader exists
            t = node_info['timeout']
            leaderexists = 0 #toggle leaderexists back  
        else: #if leader stops existing, end countdown
            t -= 1
            print(f"{t} seconds left until I run for office")

        time.sleep(1)    
    
    #switch to candidate state
    print("Beginning Inseurrection")
    node_info['state'] = 'c'
    threading.Thread(target=candidate, args=[socket]).start()

#handles all messages
def message_handle(msg_in,socket) -> None:
    #set gloal variables
    global leaderexists, node_info, group, name, port, termvotes, msg, current_leader
    msg_c = msg
    #Decodemessage
    dm = json.loads(msg_in.decode('utf-8'))
    Request = dm['request']
    
    #node recieving its own message, don't handle it
    if dm['sender_name'] == name:
        print(f"Got my own message")
    #node is not recipient, don't handle it
    elif dm['recipient'] != "E" and dm['recipient'] != name:
        print(f"Message isnt for me: {dm}")
    #node recieving command from controller
    elif dm['sender_name'] == "Controller":
        #UPDATE
        if Request == 'STATUS':
            send_message(node_info,'Controller',socket,port)
        #turn node into a follower
        elif Request == 'FOLLOW':
            #change state to follower
            node_info['state'] = 'f'
        #turn node into a candidate
        elif Request == 'TRYLEAD':
            if node_info['state'] != 'l':
                leaderexists = 0
        #have node play dead
        elif Request == 'PLAYDEAD':
            node_info['state'] = 'd'
        #Add something to the log
        elif Request == 'STORE':
            if node_info['state'] == 'l':#store what controller wants
                storethis = {'term':node_info['term'],'key':dm['key'],'value':dm['value']}
                print(f"store the stuff controller wants: {storethis}")
                node_info['log'].append(storethis)
                #broadcasting appendrpc
                msg_c['sender_name'] = name
                msg_c['request'] = 'HEARTBEAT'
                msg_c['recipient'] = 'E'
                msg_c['term'] = node_info['term']
                msg_c['prev_log_term'] = node_info['log'][len(node_info['log'])-2]['term']
                msg_c['prev_log_term'] = len(node_info['log'])-2
                msg_c['commit_index'] = len(node_info['log'])
                msg_c['entry'] = storethis
                send_message(msg_c,group,socket,port)

            else:#send leader_info to controller
                msg_c["request"]= 'LEADER_INFO'
                msg_c["key"] = "LEADER"
                msg_c["value"] = current_leader
                send_message(msg_c,"Controller",socket,port)
        #Retrieve Logs
        elif Request == 'RETRIEVE':
            if node_info['state'] == 'l':#store what controller wants
                msg_c["request"]= 'RETRIEVE'
                msg_c["key"] = "COMMITED_LOGS"
                msg_c["value"] = node_info['log']
                send_message(msg_c,"Controller",socket,port)
            else:#send leader_info to controller
                msg_c["request"]= 'LEADER_INFO'
                msg_c["key"] = "LEADER"
                msg_c["value"] = current_leader
                send_message(msg_c,"Controller",socket,port)

    #node recieving message from other node
    elif node_info['state'] != 'd':
        #follower recieving a candidate's vote request 
        if Request== "VOTEME":
            #if you havent voted yet, and the candadites logs are valid, give up your vote
            if node_info['votedFor'] == '' and dm['term'] >= node_info['term'] and len(node_info['log'])-1 <= dm['prev_log_term']:#vote yes
                    msg_c['request'] = "LEADME"
                    node_info['votedFor'] = dm['sender_name']
                    print(f"Voted for {dm['sender_name']}")
            else:#vote no
                msg_c['request'] = "!LEADME"
                print(f"Im not voting for {dm['sender_name']}!!")
            #send out message
            msg_c['sender_name'] = name
            msg_c['recipient'] = dm['sender_name']
            send_message(msg_c,group,socket,port)
        #candidate recieving a follower's vote respopnse     
        elif Request == "LEADME":
            print(f"{dm['sender_name']} voted for me!!")
            termvotes += 1
        #candidate recieving a follower's vote respopnse  
        elif Request == "!LEADME":
            print(f"{dm['sender_name']} is a hater")
        #follower recieving a leader's heartbeat
        elif Request == "LAGGING":
            msg_c["request"]= 'LEADER_INFO'
            msg_c["key"] = "LEADER"
            msg_c["value"] = current_leader
            msg_c['recipient'] = dm['sender_name']
            send_message(msg_c,group,socket,port)
        elif Request == "LEADER_INFO" and dm['recipient'] == name:
            find_leader.append(msg_c['value'])
        elif Request == "HEARTBEAT":
            #verify heartbeat
            if dm['term'] >= node_info['term'] and node_info['log'][dm['prev_log_index']]['term'] <= dm['prev_log_term']:
                leaderexists = 1
                node_info['term'] = dm['term']
                termvotes = 0
                node_info['state'] ='f'               
                node_info['votedFor'] = ''
                print(f"All hail {dm['sender_name']}")
                #if heartbeat has a log, add it to follower's log
                if dm['entry']:
                    node_info['log'].append(dm['entry'])
                #send a success msg to leader
                msg_c['request'] = "Append_Reply"
                msg_c['recipient'] = dm['sender_name']
                msg_c['success'] = 'true'
                send_message(msg_c,group,socket,port)
            else:#invalid heartbeat     
                print(f"invalid heartbeat: {dm['sender_name']}") 
                #send a failure msg to leader       
                msg_c['request'] = "Append_Reply"
                msg_c['recipient'] = dm['sender_name']
                msg_c['success'] = 'false'
                send_message(msg_c,group,socket,port)
                #get consensus on who leader is
                msg_c['request'] = "LAGGING"
                msg_c['recipient'] = 'E'
                send_message(msg_c,group,socket,port)
                #wait a few in this message thread while nodes respond
                time.sleep(2)
                #choose most popular leader as current leader
                countup = {}
                most =0
                lea = ''
                for l in find_leader:
                    if l in countup:
                        countup[l] += 1
                        if countup[l] >= most:
                            most = countup[l]
                            lea = l
                    else:
                        countup.append({l:0})
                current_leader = lea
                #send catchup request to leader
                msg_c['request'] = "CATCHMEUP"
                msg_c['recipient'] = current_leader
                send_message(msg_c,group,socket,port)
        #Lagging node to Leader
        elif Request == "CATCHMEUP":
            
        #Candidates checking for new leader
        elif Request == "VOTECONCENSUS":
            if dm['key'] == 'votes':
                termcandidates[dm['sender_name']] = dm['value']
        #Bad Message
        else:
            print(f"Bad Message @{Request}")
    #node is dead
    else:
        print("Do Not Disturb")


if __name__ == "__main__":
    print(f"Starting "+ name)

    time.sleep(10) #Give controller some time to start up
    
    print("Building Multicast socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    time.sleep(3)
    
    #All nodes begin as followers
    threading.Thread(target=follow, args=[sock]).start()

    print("Listening ...")
    while True:
        mesg = 0
        try:
            mesg, addr = sock.recvfrom(1024)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")

         #Messages are handled by creating threads
        if mesg:
            threading.Thread(target=message_handle, args=[mesg,sock]).start()