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
port = int(os.getenv('Port')) or 5555
group = os.getenv('group')
tor1 = int(os.getenv('tor1'))
tor2 = int(os.getenv("tor2"))
heartrate = float(os.getenv("heartrate"))
client_host = os.getenv("client_host")
client_port = int(os.getenv("client_port"))
#print(f"Global variables:\nname:{name}\nport:{port}\ngroup:{group}\ntor1:{tor1}\ntor2:{tor2}\nheartrate:{heartrate}\nclient_host:{client_host}\nclient_port:{client_port}")

#RAFT Variables
leaderexists = 0
termvotes=0
termcandidates = {}
current_leader = ''
find_leader = []

#other global vars
chat_history = ['Welcome all']

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

#set up lead functionality
def lead(socket) -> None:
    #set gloal variables
    global chat_history, current_leader, leaderexists, termcandidates, group, node_info, name, port, termvotes
    msg_c = msg
    msg_c['sender_name'] = name
    node_info['votedFor'] = ''
    current_leader = name
    leaderexists = 1
    termvotes = 0
    termcandidates = {}
    heartbeat = node_info['heartbeat_interval'] 
    print(name+ " is now a leader")
    
    print(name+ " running client application")  
    #client app # app = setup_app() ; run_client(client_host,client_port,app[0],app[1])
    
    print(name+ " Sending Heartbeats")  
    while node_info['state'] == 'l':
        #send heartbeats
        msg_c['request'] = 'HEARTBEAT'
        msg_c['recipient'] = 'E'
        msg_c['term'] = node_info['term']
        msg_c['prev_log_term'] = node_info['log'][len(node_info['log'])-1]['term']
        msg_c['prev_log_term'] = len(node_info['log'])-1
        msg_c['commit_index'] = len(node_info['log'])
        msg_c['entry'] = None
        send_message(msg_c,group,socket,port)
        time.sleep(heartbeat)
    
    print("Resigning from Leadership")
    # kill client application
    #kill_client()
    
#set up candidate functionality
def candidate(socket) -> None:
    #set gloal variables
    global leaderexists,node_info, group, name, port, termvotes, current_leader
    node_info['term'] += 1
    node_info['votedFor'] = ''
    current_leader = ''
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

    #wait a bit  for votes to come in
    time.sleep(1)
    if node_info['state'] == 'f': # if recieved a valid heartbeat, switch to follow state
        threading.Thread(target=follow, args=[socket]).start()
        return
    
    #let other candidates know aboout votes\
    msg_c['request'] = "VOTECONCENSUS"
    msg_c['recipient'] = 'E'
    msg_c['key'] = 'votes'
    msg_c['value'] = termvotes
    send_message(msg_c,group,socket,port)
    
    print("waiting for concensus")
    while len(termcandidates) == 0:             
        time.sleep(1)

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
    time.sleep(t) # give leader a second
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
    global leaderexists, node_info, group, name, port, termvotes, msg, current_leader, find_leader
    msg_c = msg
    msg_c['sender_name'] = name
    #Decodemessage
    dm = json.loads(msg_in.decode('utf-8'))
    Request = dm['request']
    
    #node recieving its own message, don't handle it
    if dm['sender_name'] == name:
        time.sleep(.25)
    #node is not recipient, don't handle it
    elif dm['recipient'] != "E" and dm['recipient'] != name:
        time.sleep(.25)
    #node recieving command from controller
    elif dm['sender_name'] == "Controller":
        #UPDATE
        if Request == 'STATUS':
            msg_c['recipient'] = 'Controller'
            msg_c['request'] = "STATUS"
            msg_c['key'] = 'Node_Info'
            msg_c['value'] = node_info
            send_message(msg_c,group,socket,port)
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
            if node_info['state'] == 'l':
                node_info['state'] = 'd'
        #Add something to the log
        elif Request == 'STORE':
            if node_info['state'] == 'l':#store what controller wants
                storethis = {'term':node_info['term'],'key':dm['key'],'value':dm['value']}
                print(f"store the stuff controller wants: {storethis}")
                node_info['log'].append(storethis)
                #broadcasting appendrpc
                msg_c['request'] = 'HEARTBEAT'
                msg_c['recipient'] = 'E'
                msg_c['term'] = node_info['term']
                msg_c['prev_log_term'] = node_info['log'][len(node_info['log'])-2]['term']
                msg_c['prev_log_term'] = len(node_info['log'])-2
                msg_c['commit_index'] = len(node_info['log'])
                msg_c['entry'] = storethis
                send_message(msg_c,group,socket,port)
                print(f"New log:{node_info['log']}")
            else:#send leader_info to controller
                print("Sending LEADER_INFO to controller")
                msg_c['request']= 'LEADER_INFO'
                msg_c['recipient'] = 'Controller'
                msg_c['key'] = "LEADER"
                msg_c['value'] = current_leader
                send_message(msg_c,group,socket,port)
        #Retrieve Logs
        elif Request == 'RETRIEVE':
            if node_info['state'] == 'l':#store what controller wants
                msg_c['request']= 'RETRIEVE'
                msg_c['key'] = "COMMITED_LOGS"
                msg_c['recipient'] = 'Controller'
                msg_c['value'] = node_info['log']
                send_message(msg_c,group,socket,port)
            else:#send leader_info to controller
                msg_c['request']= 'LEADER_INFO'
                msg_c['key'] = "LEADER"
                msg_c['value'] = current_leader
                msg_c['recipient'] = 'Controller'
                send_message(msg_c,group,socket,port)

    #node recieving message from other node
    elif node_info['state'] != 'd':
        #follower recieving a candidate's vote request 
        if Request== "VOTEME":
            print(f"Vote request: {dm} \n My State: {node_info}")
            #if you havent voted yet, and the candadites logs are valid, give up your vote
            if node_info['votedFor'] == '' and dm['term'] >= node_info['term'] and dm['prev_log_index'] >= len(node_info['log'])-1:#vote yes
                    msg_c['request'] = "LEADME"
                    node_info['votedFor'] = dm['sender_name']
                    print(f"Voted for {dm['sender_name']}")
            else:#vote no
                msg_c['request'] = "!LEADME"
                print(f"Im not voting for {dm['sender_name']}!!")
            #send out message
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
        elif Request == "HEARTBEAT":
            #verify heartbeat
            if dm['prev_log_index'] > len(node_info['log']):#Lagger
                #get consensus on who leader is
                msg_c['request'] = "LAGGING"
                msg_c['recipient'] = 'E'
                send_message(msg_c,group,socket,port)
                #wait a few in this message thread while nodes respond
                time.sleep(1)
                #choose most popular leader as current leader
                print(f"Possible Leaders: {find_leader}")
                countup = {}
                most =0
                lea = ''
                for l in find_leader:
                    count = countup
                    if l in count:
                        countup[l] += 1
                        if countup[l] >= most:
                            most = countup[l]
                            lea = l
                    else:
                        countup[l]=0
                current_leader = lea
                #send catchup request to leader
                find_leader = []
                msg_c['request'] = "CATCHMEUP"
                msg_c['recipient'] = current_leader
                send_message(msg_c,group,socket,port)
            elif dm['term'] >= node_info['term'] and node_info['log'][dm['prev_log_index']]['term'] <= dm['prev_log_term']:
                leaderexists = 1
                node_info['term'] = dm['term']
                termvotes = 0
                node_info['state'] ='f'               
                current_leader = dm['sender_name']
                node_info['votedFor'] = ''
                #print(f"All hail {dm['sender_name']}")
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
                
        #Node recieving message from Lagging Node
        elif Request == "LAGGING":
            if current_leader != '':
                msg_c['request']= 'LEADER_INFO'
                msg_c['key'] = "LEADER"
                msg_c['value'] = current_leader
                msg_c['recipient'] = dm['sender_name']
                send_message(msg_c,group,socket,port)
        #From node to Lagging Node
        elif Request == "LEADER_INFO" and dm['recipient'] == name:
            if msg_c['value']:
                find_leader.append(msg_c['value'])
        #Lagging node to Leader
        elif Request == "CATCHMEUP":
            #send entire log history to lagger
            msg_c['request'] = "CATCHUP"
            msg_c['recipient'] = current_leader
            msg_c['key'] = 'Logs'
            msg_c['value'] = node_info['log']
            send_message(msg_c,group,socket,port)
        #Leader trying to CATCHUP Lagging Node
        elif Request == "CATCHUP":
            #update log with leaders log
            if dm['sender_name'] == current_leader:
                node_info['log'] = msg_c['value']
                leaderexists = 1
        #Candidates checking for new leader
        elif Request == "VOTECONCENSUS":
            if dm['key'] == 'votes':
                termcandidates[dm['sender_name']] = dm['value']
        #Append_Reply from followers to leader
        elif Request == "Append_Reply":
            if name == dm['recipient'] and name == current_leader:
                if dm['success'] == 'true':
                    print(f'{dm["sender_name"]} Loves me :)')
                else:
                    print(f'{dm["sender_name"]} Hates me :(')
        #Bad Message
        else:
            print(f"Bad Message @{Request}")
    #node is dead
    else:
        print("Do Not Disturb")


if __name__ == "__main__":
    print(f"Starting "+ name)

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
            mesg, addr = sock.recvfrom(2048)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")

         #Messages are handled by creating threads
        if mesg:
            threading.Thread(target=message_handle, args=[mesg,sock]).start()
