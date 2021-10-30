# This file attempts to listen in on the communications of the MIL Bus and log activity in a .json file

# This file is a WORK IN PROGRESS
# ToDo:
# Replace example event with actual code that gets an event from the simulator
# Loop execution so the logging occurs continuously as long as the program is left running
import socket
import threading
import json
import time
from datetime import datetime

# Copy BC_Listener class from Bus_Controller.Physical_Layer_Emulation.Communication_Socket_BC.py and edit
class BC_Listener:

    data_received = list()

    def start_listening(self):
        port = 2000
        socket_variable = \
            socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        socket_variable.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        socket_variable.bind(("", port))
        while True:
            data, addr = socket_variable.recvfrom(1024)
            self.data_received.append(str(data))

# Function to add date and time information to a log entry
def addtime ( dictionary ) :
    "This takes a dictionary and adds entries for the date and time of function call"
    now = datetime.now()
    dictionary['time_year'] = now.strftime('%Y')
    dictionary['time_month'] = now.strftime('%m')
    dictionary['time_day'] = now.strftime('%d')
    dictionary['time_hour'] = now.strftime('%H')
    dictionary['time_minute'] = now.strftime('%M')
    dictionary['time_second'] = now.strftime('%S')
    return

def logevent ( event ) :
    "This takes an event of received data, parsed as a dictionary, and logs it"
    # Name of file should be from date
    addtime(event)
    now = datetime.now()
    jsonfilename = now.strftime('%m-%d-%Y_log.json')
    # Output of event to json
    with open(jsonfilename, 'a') as event_dumped :
        json.dump(event, event_dumped)

if __name__ == "__main__":
    # Example dict of event to log
    event_EX = {
        'flag1' : '01',
        'flag2' : '11',
        'length' : '07'
    }
    logevent(event_EX)