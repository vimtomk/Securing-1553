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
    def __init__(self, terminal, sync_freq, filename = "Not set"):
        '''This is the default initializer of the bus monitor object'''
        # Initialize BM variables
        self.num                = BitArray(uint=terminal, length=5) # Value indicating the terminal the bus monitor is listening from
        self.current_filename   = filename                          # String containing the name of the .json to log events to
        self.frequency          = sync_freq                         # Time, in seconds, of how often the bus is checked
        self.last_message       = None                              # Keeps track of the last message on the bus, to see if it changed
        # For Timer functions, create a variable to check if the object still exists before looping execution
        self.exists = "Yes!"
        # Correct the filename if it lacks ".json", and is not the default case
        if(self.current_filename != "Not set"):
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
        if(self.exists == "Yes!"):
            threading.Timer(self.frequency, self.record_bus_contents).start()
        else:
            return
        tmp_message = self.bus.read_BitArray()
        # Is there anything new on the bus?
        if(tmp_message == self.last_message):
            # Probably nothing new to log, ignore what is on the bus
            # Possibly add some logic here to make sure valid duplicate data words are still logged?
            #--- MAYBE Add some logic somewhere that clears the bus (0x00000) before write time every time???
            return
        # Else, there is something new to log. So do that.
        bus_event = {}
        bus_event["Raw Message"] = tmp_message
        self.addtime(bus_event)
        if(tmp_message[0] == 1 and tmp_message[1] == 1 and tmp_message[2] == 0): # If a data word 110...
            bus_event["Message Type"] = "Data"
            bus_event["Data Word"] = chr(int(tmp_message.bin[3:11],2)) + chr(int(tmp_message.bin[11:19],2))
        elif(tmp_message[0] == 1 and tmp_message[1] == 0 and tmp_message[2] == 1): # If a command word 101...
            bus_event["Message Type"] = "Command"
            bus_event["Recipient RT"] = int("0b" + tmp_message.bin[3:8], 2)
            bus_event["T(1)/R(0) Bit"] = tmp_message.bin[8]
            if((tmp_message[9:14] == "00000") or tmp_message[9:14] == "11111"): # If subaddress field is either of these, it is a mode code in the next 5-bit field
                bus_event["Command Type"] = "Mode Code"
                bus_event["Mode Code Raw"] = tmp_message.bin[14:19]
            else:
                bus_event["Command Type"] = "Word Count"
        elif(tmp_message[0] == 1 and tmp_message[1] == 1 and tmp_message[2] == 1): # If a status word 111...
            bus_event["Message Type"] = "Status"
            bus_event["Recipient RT"] = int("0b" + tmp_message.bin[3:8], 2)
            bus_event["Message Error Flag"] = tmp_message[8]
            bus_event["Service Request Flag"] = tmp_message[10]
            bus_event["Busy Bit"] = tmp_message[15]
        else:
            bus_event["Message Type"] = "Error"
        if(tmp_message.count(1) % 2 == 0):
            bus_event["Parity"] = "Failed"
        else:
            bus_event["Parity"] = "Passed"
        # Any other things that need to be logged to the json should probably be recorded here.
        ##TODO: Fix attempted logging of "BitArray" type events. BitArray must be converted to something else
        #self.log_to_json(bus_event)
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
        return

    def main(self):
        '''Main function'''
        if(self.current_filename == "Not set"):
            self.defualt_filename_to_date()
        self.record_bus_contents()
        return
    
    # BM Destructor
    def __del__(self):
        '''This is the destructor of the BM object.'''
        self.exists = "No."
        del(self)