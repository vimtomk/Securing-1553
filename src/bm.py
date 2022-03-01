#!/usr/bin/env python3

from bus import bus
from time import sleep
from datetime import datetime
from bitstring import BitArray
from os import getcwd
import threading
import json

class bm(object):
    # BM Constructor
    def __init__(self, terminal, sync_freq):
        '''This is the default initializer of the bus monitor object'''
        # Initialize BM variables
        self.num                = BitArray(uint=terminal, length=5) # Value indicating the terminal the bus monitor is listening from
        self.current_filename   = 'Not yet set'                     # String containing the name of the .json to log events to
        self.frequency          = sync_freq                         # Time, in seconds, of how often the bus is checked
        self.last_message       = None                              # Keeps track of the last message on the bus, to see if it changed
        # Begin normal BM behavior
        self.bus = bus()
        self.main()

    # BM Constructor, with filename pre-defined by function input
    def __init__(self, terminal, sync_freq, filename):
        '''This is the argumented initializer of the bus monitor object, setting a custom filename for the resulting json'''
        # Initialize BM variables
        self.num                = BitArray(uint=terminal, length=5) # Value indicating the terminal the bus monitor is listening from
        self.current_filename   = filename                          # String containing the name of the .json to log events to
        self.frequency          = sync_freq                         # Time, in seconds, of how often the bus is checked
        self.last_message       = None                              # Keeps track of the last message on the bus, to see if it changed
        # Correct the filename if it lacks ".json"
        if(len(self.current_filename) < 6):
            self.current_filename.append('.json')
        elif(self.current_filename[-5:] != '.json'):
            self.current_filename.append('.json')
        # Begin normal BM behavior
        self.bus = bus()
        self.main()

    def return_terminal_num(self):
        '''This returns the value of the remote terminal this BM object is meant to act through'''
        return self.num
    
    # Sets a defualt filename. Only run if none is given on init.
    def defualt_filename_to_date(self):
        '''This will set the name of the log file to the current date'''
        temp_dt = datetime.now()
        #enum_months = enumerate({ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'}) # Not needed???
        self.current_filename = temp_dt.strftime('%d-%m-%Y_log.json')
        return

    # Recursive function to periodically record the contents of the bus.
    def record_bus_contents(self):
        '''This will get the contents of the bus and record it every so often'''
        threading.Timer(self.frequency, self.record_bus_contents).start()
        tmp_message = bus.read_BitArray()
        # Is there anything new on the bus?
        if(tmp_message == self.last_message):
            # Probably nothing new to log, ignore what is on the bus
            #TODO: Possibly add some logic here to make sure valid duplicate data words are still logged?
            #--- MAYBE Add some logic somewhere that clears the bus (0x00000) before write time every time???
            return
        # Else, there is something new to log. So do that.
        bus_event = {}
        bus_event["Raw Message"] = self.tmp_message
        self.addtime(bus_event)
        if(tmp_message[0] == 1 and tmp_message[1] == 1 and tmp_message[2] == 0): # If a data word 110...
            bus_event["Message Type"] = "Data"
            bus_event["Data Word"] = chr(int(tmp_message.bin[3:11],2)) + chr(int(tmp_message.bin[11:19],2))
        elif(tmp_message[0] == 1 and tmp_message[1] == 0 and tmp_message[2] == 1): # If a command word 101...
            bus_event["Message Type"] = "Command"
            #TODO: Check if it's an actual command in the mode code or a count of data words to send
            bus_event["Mode Code"] = tmp_message.bin[14:19]
            #TODO: Add field for recipient, and other relevent data
        elif(tmp_message[0] == 1 and tmp_message[1] == 1 and tmp_message[2] == 1): # If a status word 111...
            bus_event["Message Type"] = "Status"
            #TODO: Parse out relevent fields to log 
        #TODO: Any other things that need to be logged to the json should probably be recorded here...
        # Keep a temporary copy of the last message for future comparisons.
        self.last_message = tmp_message
        return

    def log_to_json(self, event):
        '''This takes an event of received data, as a dictionary, and logs it'''
        with open(getcwd() + '/io/jsons/' + self.current_filename, 'a') as event_dumped :
            json.dump(event, event_dumped)
        return

    def addtime(self, dictionary):
        '''This takes a dictionary and adds entries for the approximate date and time of function call, down to the microsecond'''
        temp_dt = datetime.now()
        dictionary['time_year'] = temp_dt.strftime('%Y')
        dictionary['time_month'] = temp_dt.strftime('%m')
        dictionary['time_day'] = temp_dt.strftime('%d')
        dictionary['time_hour'] = temp_dt.strftime('%H')
        dictionary['time_minute'] = temp_dt.strftime('%M')
        dictionary['time_second'] = temp_dt.strftime('%S')
        dictionary['time_microsecond'] = temp_dt.strftime('%f')

    def main(self):
        '''Main function'''
        if(self.current_filename == 'Not yet set'):
            self.defualt_filename_to_date()
        self.record_bus_contents()
    
    # BM Destructor
    def __del__(self):
        '''This is the destructor of the BM object. It just does del(self)'''
        del(self)