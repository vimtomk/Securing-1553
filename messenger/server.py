# This file is to be run on the "server" side of the bus (the one accepting a connection)
# This file should be run alongside the server.py file to communicate!

# Socket-related files are a Work-In-Progress, and shouldn't be run in VSCode! They are being developed and run on other machines, and are copy-pasted here periodically.

import socket

server_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # Simulator requires DGRAM type and UDP protocol
server_.bind((socket.gethostname(), 2001)) # Simulator declares port 2001 for sending FROM BUS, so we take in from this port

# To-Do : Implement MIL-STD-1553 standards for encoding, packetization, port numbers, etc... in this code file and its partner "client.py"