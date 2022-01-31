#!/usr/bin/env python3

from message import message, command_word, data_word, status_word
from bus import Bus, databus
from time import sleep
from bitstring import Bits, BitArray

class bm(object):
    # BM Constructor
    def __init__(self, terminal):
        # Initialize BM variables
        self.num                = BitArray(uint=terminal, length=5)   # Value indicating the terminal the bus monitor is listening from
        
        # Begin normal BM behavior
        self.main()

    # Returns the terminal number of the BC
    def return_terminal_num(self):
        return self.num

    #def record_bus_contents(self):

    # Define other functions of a BM here

    #def main(self):
    #    while(1):  
            # Define the behavior of a BM here
    
    # BM Destructor
    def __del__(self):
        del(self)