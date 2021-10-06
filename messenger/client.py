# This file is to be run on the "client" side of the bus (the one requesting a connection)
# This file should be run alongside the server.py file to communicate!

# Socket-related files are a Work-In-Progress, and shouldn't be run in VSCode! They are being developed and run on other machines, and are copy-pasted here periodically.

import socket

client_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # MODIFY TO MEET MIL-STD-1553
client_.connect((socket.gethostname(), 1234)) # MODIFY TO MEET MIL-STD-1553 & MATCH SYSTEM REQ.

# To-Do : Implement MIL-STD-1553 standards for encoding, packetization, port numbers, etc... in this code file and its partner "server.py"