#!/usr/bin/env python3

from message import message, command_word, data_word, status_word
from bus import Bus, databus
from time import sleep
from bitstring import Bits, BitArray
import queue

class bc(object):
    # BC Constructor
    def __init__(self, terminal):
        # Initialize BC variables
        self.num                = BitArray(uint=terminal, length=5)   # Value indicating the terminal the bus controller is operating from
        
        # Begin normal BC behavior
        self.main()

    # Returns the terminal number of the BC
    def return_terminal_num(self):
        return self.num
    
    #def issue_command_word(self, target_rt, ...):
        #databus.add_message(sendable_command_word)

    #def validate_status_word(self, status_word):

    #def validate_data_word(self, data_word):

    # Define other functions of a BC here

    #def main(self):
    #    while(1):  
            # Define the behavior of a BC here
    
    # BC Destructor
    def __del__(self):
        del(self)