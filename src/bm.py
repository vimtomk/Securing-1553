#!/usr/bin/env python3

from message import message, command_word, data_word, status_word
from bus import Bus, databus
from time import sleep
from bitstring import Bits, BitArray
from datetime import datetime
from os import getcwd
import json

class bm(object):
    # BM Constructor
    def __init__(self, terminal):
        # Initialize BM variables
        self.num                = BitArray(uint=terminal, length=5)     # Value indicating the terminal the bus monitor is listening from
        self.current_filename   = 'Not yet set'                         # String containing the name of the .json to log events to
        self.temp_dt      = datetime.now                          # Acts as a temporary holder for any datetime usage
        # Begin normal BM behavior
        self.main()

    # BM Constructor, with filename pre-defined
    def __init__(self, terminal, filename):
        # Initialize BM variables
        self.num                = BitArray(uint=terminal, length=5)     # Value indicating the terminal the bus monitor is listening from
        self.current_filename   = filename                              # String containing the name of the .json to log events to
        self.temp_datetime      = datetime.now                          # Holds the datetime
        # Begin normal BM behavior
        self.main()

    # Returns the terminal number of the BC
    def return_terminal_num(self):
        '''This returns the value of the remote terminal this BC object is meant to act through'''
        return self.num
    
    def defualt_filename_to_date(self):
        '''This will set the name of the log file to the current date'''
        temp_dt = datetime.now()
        enum_months = enumerate({ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'})
        filename = temp_dt.strftime('%d-%m-%Y_log.json')
        del enum_months
        return

    #def record_bus_contents(self):

    def log_to_json(self, event, filename):
        '''This takes an event of received data, as a dictionary, and logs it'''
        with open(getcwd() + '/io/jsons/' + filename, 'a') as event_dumped :
            json.dump(event, event_dumped)
        return

    def addtime (self, dictionary) :
        '''This takes a dictionary and adds entries for the date and time of function call'''
        now = datetime.now()
        dictionary['time_year'] = now.strftime('%Y')
        dictionary['time_month'] = now.strftime('%m')
        dictionary['time_day'] = now.strftime('%d')
        dictionary['time_hour'] = now.strftime('%H')
        dictionary['time_minute'] = now.strftime('%M')
        dictionary['time_second'] = now.strftime('%S')
        dictionary['time_microsecond'] = now.strftime('%f')
        
    # Define other functions of a BM here

    #def main(self):
        #while(1):
            #if(self.current_filename == 'Not yet set'):
                #defualt_filename_to_date()
            # Define the behavior of a BM here
    
    # BM Destructor
    def __del__(self):
        del(self)