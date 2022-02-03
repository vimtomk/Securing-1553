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
        self.temp_dt            = datetime.now                      # Acts as a temporary holder for any datetime usage
        self.frequency          = sync_freq                         # Time, in seconds, of how often the bus is checked
        self.tmp_message        = None                              # Holds the message being processed
        self.last_message       = None                              # Keeps track of the last message on the bus, to see if it changed
        # Begin normal BM behavior
        self.bus = bus()
        self.main()

    # BM Constructor, with filename pre-defined by function input
    def __init__(self, terminal, sync_freq, filename):
        '''This is the argumented initializer of the bus monitor object, setting a custom filename for the log'''
        # Initialize BM variables
        self.num                = BitArray(uint=terminal, length=5) # Value indicating the terminal the bus monitor is listening from
        self.current_filename   = filename                          # String containing the name of the .json to log events to
        self.temp_dt            = datetime.now                      # Acts as a temporary holder for any datetime usage
        self.frequency          = sync_freq                         # Time, in seconds, of how often the bus is checked
        self.tmp_message        = None                              # Holds the message being processed
        self.last_message       = None                              # Keeps track of the last message on the bus, to see if it changed
        # Correct the filename if it lacks ".json"
        if(len(self.current_filename) < 6):
            self.current_filename.append('.json')
        elif(self.current_filename[-5:] != '.json'):
            self.current_filename.append('.json')
        # Begin normal BM behavior
        self.bus = bus()
        self.main()

    # Returns the terminal number of the BC
    def return_terminal_num(self):
        '''This returns the value of the remote terminal this BC object is meant to act through'''
        return self.num
    
    def defualt_filename_to_date(self):
        '''This will set the name of the log file to the current date'''
        self.temp_dt = datetime.now()
        enum_months = enumerate({ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'})
        self.current_filename = self.temp_dt.strftime('%d-%m-%Y_log.json')
        return

    def record_bus_contents(self):
        '''This will get the contents of the bus and record it every so often'''
        threading.Timer(self.frequency, self.record_bus_contents).start()
        self.tmp_message = bus.read_BitArray()
        # Is there anything new on the bus?
        if(self.tmp_message == self.last_message):
            # Nothing new to log, ignore what is on the bus
            return
        # Else, there is something new to log
        bus_event = {}
        bus_event["Message"] = self.tmp_message
        self.addtime(bus_event)

        pass #TODO:Add code to log a message from the bus

        # Keep a temporary copy of the last message for future comparisons
        self.last_message = self.tmp_message
        return

    def log_to_json(self, event):
        '''This takes an event of received data, as a dictionary, and logs it'''
        with open(getcwd() + '/io/jsons/' + self.current_filename, 'a') as event_dumped :
            json.dump(event, event_dumped)
        return

    def addtime (self, dictionary) :
        '''This takes a dictionary and adds entries for the date and time of function call'''
        self.temp_dt = datetime.now()
        dictionary['time_year'] = self.temp_dt.strftime('%Y')
        dictionary['time_month'] = self.temp_dt.strftime('%m')
        dictionary['time_day'] = self.temp_dt.strftime('%d')
        dictionary['time_hour'] = self.temp_dt.strftime('%H')
        dictionary['time_minute'] = self.temp_dt.strftime('%M')
        dictionary['time_second'] = self.temp_dt.strftime('%S')
        dictionary['time_microsecond'] = self.temp_dt.strftime('%f')

    def main(self):
        '''Main function'''
        if(self.current_filename == 'Not yet set'):
            self.defualt_filename_to_date()
        self.record_bus_contents()
    
    # BM Destructor
    def __del__(self):
        '''This is the destructor of the BM object'''
        del(self)