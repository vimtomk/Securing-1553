#!/usr/bin/env python3

from message import message
from bus import Bus, databus
from time import sleep
from bitstring import Bits, BitArray
import queue
class rt(object):
    
    # RT Constructor - number is to assign RT number
    def __init__(self, number):
        self.__init__(self)
        self.num = number
        self.received_data = queue.Queue()
        # Start listening immediately
        self.main()

    # Returns the Remote Terminal ID number (0-31)
    def return_rt_num(self):
        return self.num
    
    ## TODO: Generate key-pair when BC class finished
    def gen_key(self):
        return

    # Main loop for listening to bus.
    def main(self):
        #listen or smthn idk
        while(1):
            
            # Grabs first message from bus if bus not empty
            if not(databus.is_empty()):
                tmp_msg = databus.return_first_message()
                
                # Use RT method that passes bus queue to RT and processes the first message on the queue
                if tmp_msg.msg_type.bin == "101":
                    if tmp_msg.rt_addr == self.num:
                    # This message is for this RT
                        return

                else:
                    return

            # Databus is either empty, or we are done getting messages so sleep.
            sleep(0.25) # Currently configured : Check each quarter second.
 

    # RT Destructor
    def __del__(self):
        del(self)

