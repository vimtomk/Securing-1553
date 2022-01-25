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
        self.rx_tx_mode         = 0     # RT starts off cleared (Receiving mode), and is set for transmit mode
        self.received_data = list()     # A list of the received messages used in context
                                        # to keep track of data needed for sent status words.
        self.message_error      = 0     # Error bit. Set when a word fails an RT validity test
            # Condition 1 : RT receives a word with an error
            # Condition 2 : RT expects a stream of data words, but there is a gap
            # Condition 3 : RT receives a command it does not have the functionality to execute
            # Condition 4 : RT somehow receives the wrong number of data words
        self.instrumentation    = 0     # One bit flag, always 0 when transmitting a status word
        self.service            = 0     # Service request bit. We will not use this functionality
        self.broadcast_command  = 0     # Broadcast command bit. We will not use this functionality
        self.busy               = 0     # Busy bit. Set if the BC commands the RT not to act
        self.subsystem          = 0     # Indicates subsystem. We will not use this functionality
        self.dynamic_bus        = 0     # Set if turned into a dynamic BC.
        self.terminal           = 0     # Set if this RT has a problem. Cleared on resolution.
        
        # Start listening immediately
        self.main()

    # Returns the Remote Terminal ID number (0-31)
    def return_rt_num(self):
        return self.num
    
    ## TODO: Generate key-pair when BC class finished
    def gen_key(self):
        return


    ## TODO: Create a function that will process a given mode code from command words
    def process_mode_code(self, mode_code):
        """
        switch (mode_code) {
        case 0:  Dynamic Bus Control
        case 1:  Synchronize (without a data word)
        case 2:  Transmit Status Word
        case 3:  Initiate Self Test
        case 4:  Transmitter Shutdown
        case 5:  Override Transmitter Shutdown
        case 6:  Inhibit Terminal Flag (T/F) bit
        case 7:  Override Inhibit T/F bit
        case 8:  Reset Remote Terminal
        case 9:  Reserved
        case 10: Reserved
        case 11: Reserved
        case 12: Reserved
        case 13: Reserved
        case 14: Reserved
        case 15: Reserved
        case 16: Transmit Vector Word
        case 17: Synchronize (with data word)
        case 18: Transmit Last Command Word
        case 19: Transmit Built-in-Test (BIT) Word
        case 20: Selected Transmitter Shutdown
        case 21: Override Selected Transmitter Shutdown
        case 22: Reserved
        case 23: Reserved
        case 24: Reserved
        case 25: Reserved
        case 26: Reserved
        case 27: Reserved
        case 28: Reserved
        case 29: Reserved
        case 30: Reserved
        case 31: Reserved 
        
        }
        pass 
        """

        return


    # Main loop for listening to bus.
    def main(self):

        while(1):
            
            ## TODO: Once logic is understood for each transfer type, 
            # implement the if-else, and set up contextual decision making
            # i.e., understand what to do with the next message

            # Grabs first message from bus if bus not empty
            if not(databus.is_empty()):
                tmp_msg = databus.return_first_message()
                
                # Use RT method that passes bus queue to RT and processes the first message on the queue
                if (tmp_msg.rt_addr == self.num) and (tmp_msg.msg_type.bin == "101"): # Command Word

                    # This will set the Remote Terminal's Transfer/Receiving Mode
                    if tmp_msg.tx_rx == 1:
                            self.rx_tx_mode == 1    # This puts the Remote Terminal in Transfer mode
                    else:
                            self.rx_tx_mode == 0    # Keeps RT in Receiving mode    
                    
                    # This will set the Subaddress Mode



                    # This will tell the Remote Terminal how many data words to send or receive
                    


                        

                    return

                if (tmp_msg.rt_addr == self.num) and (tmp_msg.msg_type.bin == "111") and (self.dynamic_bus == 1): # Status Word
                    ## TODO: Once we begin implementing Dynamic BC functionality, define behavior for a received status word
                    return
                        
                if tmp_msg.msg_type.bin == "110": # Data Word
                    
                    return

                # We have encountered some type of error in the message type bits 
                # (not defined as data/command/status word)
                else:
                    ## TODO: Put in JSON file error message stating that data type is wrong
                    print("ERROR: Message Type bits indentifier incorrect (not data/command/status word)!") 
                    return

            # Databus is either empty, or we are done getting messages so sleep.
            sleep(0.25) # Currently configured : Check each quarter second.
 

    # RT Destructor
    def __del__(self):
        del(self)

