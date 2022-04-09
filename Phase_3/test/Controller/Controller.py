# print("Hello World from Controller")
# import json
# import socket
# import traceback
# import time
# import os


# print("Get env variables")
# # Get environment variables
# name = "CNTRL"
# port = 8080

# # Initialize
# sender = "Controller"
# target = "Node_1"


# print("Socket Creation and Binding")
# # Socket Creation and Binding
# skt = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# skt.bind((sender, port))

# # Wait following seconds below sending the controller request
# time.sleep(5)
# while True:
#   # Send Message
#   try:
#       # Encoding and sending the message

#       skt.sendto(b"hello from control", (target, port))
#   except:
#       #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
#       print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")
#   time.sleep(10)


import socket
import traceback
import time
import struct
import threading
group = '224.1.1.1'
port = 5004
# 2-hop restriction in network
ttl = 2

def listener(sock):
  print("Listening ...")
  time.sleep(5)
  while True:
        mesg = 0
        try:
            mesg, addr = sock.recvfrom(1024)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")

            #Messages are handled by creating threads
        if mesg:
            print(mesg)
print("Building socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,ttl)
time.sleep(2)

# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind(('', port))
# mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
if __name__ == "__main__":
  #All nodes begin as followers
  threading.Thread(target=listener, args=[sock]).start()
  while True:
    print("Sending...")
    try:
        # Encoding and sending the message
        sock.sendto(b"hello world", (group, port))
    except:
        #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
        print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")
    time.sleep(10)
