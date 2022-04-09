# print("Hello World from Nodes")
# import time
# import socket 
# import traceback

# # Get environment variables
# name =  "Node_1"
# port = 8080

# print("Hello World, "+name+ " is here trying to bond to port "+str(port))

# # Creating Socket and binding it to the target container IP and port
# UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# # Bind the node to sender ip and port
# UDP_Socket.bind((name, port))

# time.sleep(5)
# #Main thread Listening at all times
# while True:
#     mesg = 0
#     try:
#         mesg, addr = UDP_Socket.recvfrom(1024)
#     except:
#         print(f"ERROR while fetching from socket : {traceback.print_exc()}")

#         #Messages are handled by creating threads
#     if mesg:
#         print(mesg)


import socket
import struct
import time
from tokenize import group
import traceback
import threading
group = '224.1.1.1'
port = 5004

def sender(sock):
    while True:
        sock.sendto(b"Hello via Nodes", (group, port))
        time.sleep(5)

print("Building socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', port))
mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
time.sleep(3)
print("Listening ...")
if __name__ == "__main__":
    threading.Thread(target=sender, args=[sock]).start()
    while True:
        mesg = 0
        try:
            mesg, addr = sock.recvfrom(1024)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")

            #Messages are handled by creating threads
        if mesg:
            print(mesg)