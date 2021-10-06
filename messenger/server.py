# This file is to be run on the "server" side of the bus (the one accepting a connection)
# This file should be run alongside the server.py file to communicate!

# Socket-related files are a Work-In-Progress, and shouldn't be run in VSCode! They are being developed and run on other machines, and are copy-pasted here periodically.

import socket

server_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # MODIFY TO MEET MIL-STD-1553
server_.bind((socket.gethostname(), 1234)) # MODIFY TO MEET MIL-STD-1553 & MATCH SYSTEM REQ.