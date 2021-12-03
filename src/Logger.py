#!/usr/bin/python3

# This file attempts to listen in on the communications of the MIL Bus and log activity in a .json file

# This file is a WORK IN PROGRESS
# TODO: Replace example event with actual code that gets an event from the simulator CORRECTLY
import socket
import threading
import json
import time
import os
from datetime import datetime
#from Bus_Controller.Physical_Layer_Emulation.Communication_Socket_BC import BC_Listener
#from Bus_Controller.Message_Layer.ML_Decoder_BC import MessageLayerDecoderBC
from Bus_Controller.Physical_Layer_Emulation.Communication_Socket_BC import BC_Listener
from Bus_Controller.Message_Layer.ML_Decoder_BC import MessageLayerDecoderBC

global logger_thread
global eventdata

# Class that codes to listen in on communications over the bus, modification of Bus_Controller class
class Bus_Logger:

    # Function to add date and time information to a log entry
    def addtime (self, dictionary) :
        "This takes a dictionary and adds entries for the date and time of function call"
        now = datetime.now()
        dictionary['time_year'] = now.strftime('%Y')
        dictionary['time_month'] = now.strftime('%m')
        dictionary['time_day'] = now.strftime('%d')
        dictionary['time_hour'] = now.strftime('%H')
        dictionary['time_minute'] = now.strftime('%M')
        dictionary['time_second'] = now.strftime('%S')
        dictionary['time_microsecond'] = now.strftime('%f')
    
    def logevent (self, event) :
        "This takes an event of received data, parsed as a dictionary, and logs it"
        # Name of file should be from date
        self.addtime(event)
        now = datetime.now()
        jsonfilename = now.strftime('%m-%d-%Y_log.json')
        # Output of event to json
        with open(os.getcwd() + '/io/jsons/' + jsonfilename, 'a') as event_dumped :
            json.dump(event, event_dumped)

    def handle_incoming_frame(self, frame):
        self.logevent(MessageLayerDecoderBC().interprete_incoming_frame(frame))

    def start_listener(self):
        "This starts a listening thread"
        # Log start of logging
        logstart = { 'message' : 'Logging has started' }
        self.logevent(logstart)
        # Example dict of event to log (Comment out for real runs)
        #event_EX = {
        #    'flag1' : '01',
        #    'flag2' : '11',
        #    'length' : '07'
        #}
        #self.logevent(event_EX)
        listener = BC_Listener()
        listener_thread = threading.Thread(target=listener.start_listening)
        listener_thread.start()
        while True:
            if not len(listener.data_received) == 0:
                eventData = {'Message' : listener.data_received}
                self.logevent(eventData)
                listener.data_received.pop(0)

if __name__ == "__main__":
    # Log incoming data
    logger_thread = threading.Thread(target=Bus_Logger().start_listener)
    logger_thread.start()