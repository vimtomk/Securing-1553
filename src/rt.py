#!/usr/bin/env python3

from message import message, command_word, data_word, status_word
from bus import Bus, databus
from time import sleep
from bitstring import Bits, BitArray
import queue

class rt(object):
    
    # RT Constructor - number is to assign RT number
    def __init__(self, number):
        self.__init__(self)
        self.num                = BitArray(uint=number, length=5)
        self.rx_tx_mode         = "none" # RT starts off cleared (not transmitting)
                                         # and is set for transmit mode
        self.rx_tx_mode         = BitArray(uint=0, length=1) 
        self.received_data      = list() # A list of the received messages used in context
                                         # to keep track of data needed for sent status words.
        self.message_error      = 0      # Error bit. Set when a word fails an RT validity test
            # Condition 1 : RT receives a word with an error
            # Condition 2 : RT expects a stream of data words, but there is a gap
            # Condition 3 : RT receives a command it does not have the functionality to execute
            # Condition 4 : RT somehow receives the wrong number of data words
        self.instrumentation    = 0      # One bit flag, always 0 when transmitting a status word
        self.service            = 0      # Service request bit. We will not use this functionality
        self.broadcast_command  = 0      # Broadcast command bit.
        self.busy               = 0      # Busy bit. Set if the BC commands the RT not to act
        self.subsystem          = 0      # Indicates subsystem. We will not use this functionality
        self.dynamic_bus        = 0      # Set if turned into a dynamic BC.
        self.terminal           = 0      # Set if this RT has a problem. Cleared on resolution.
        
        self.last_command_word  = BitArray(uint=0, length=16)   # Use to store last received command word
        
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
        if  (mode_code==BitArray(uint=0, length=5)):	# case 0:  Dynamic Bus Control | No Data Word Associated
            return 
        
        elif (mode_code==BitArray(uint=1, length=5)):	# case 1:  Synchronize (without a data word) | No Data Word Associated
            return 

        elif (mode_code==BitArray(uint=2, length=5)):	# case 2:  Transmit Status Word | No Data Word Associated
            # Create status word from status of the RT
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            # Add  status word to the databus
            databus.add_message(sendable_status_word)
            return 

        elif (mode_code==BitArray(uint=3, length=5)):	# case 3:  Initiate Self Test |  No Data Word Associated
            return
        
        elif (mode_code==BitArray(uint=4, length=5)):	# case 4:  Transmitter Shutdown  | No Data Word Associated
            # We are not using a Dual Redundant bus system, this shouldn't do anything
            return
        
        elif (mode_code==BitArray(uint=5, length=5)):	# case 5:  Override Transmitter Shutdown | No Data Word Associated
            # We are not using a Dual Redundant bus system, this shouldn't do anything
            return
        
        elif (mode_code==BitArray(uint=6, length=5)):	# case 6:  Inhibit Terminal Flag (T/F) bit   | No Data Word Associated
            # Clear terminal flag bit FIRST
            self.terminal = 0
            # Send status word
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            databus.add_message(sendable_status_word)
            return
        
        elif (mode_code==BitArray(uint=7, length=5)):	# case 7:  Override Inhibit T/F bit  | No Data Word Associated
            # Override terminal flag bit FIRST
            self.terminal = 1
            # Send status word
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            databus.add_message(sendable_status_word)
            return
        
        elif (mode_code==BitArray(uint=8, length=5)):	# case 8:  Reset Remote Terminal | No Data Word Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            databus.add_message(sendable_status_word)
            # Reset RT values to default
            self.rx_tx              = BitArray(uint=0, length=1)
            self.message_error      = BitArray(uint=0, length=1)
            self.instrumentation    = BitArray(uint=0, length=1)
            self.service            = BitArray(uint=0, length=1)
            self.broadcast_command  = BitArray(uint=0, length=1)
            self.busy               = BitArray(uint=0, length=1)
            self.subsystem          = BitArray(uint=0, length=1)
            self.dynamic_bus        = BitArray(uint=0, length=1)
            self.terminal           = BitArray(uint=0, length=1)
            return
        
        elif (mode_code==BitArray(uint=16, length=5)):	# case 16: Transmit Vector Word | Data Word Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            databus.add_message(sendable_status_word)
            # Send data word containing bits 4-19 of the last command word this RT received, excluding mode code bits
            return
        
        elif (mode_code==BitArray(uint=17, length=5)):	# case 17: Synchronize (with data word) | Data Word Associated
        
        ## TODO: Create a data word with sychronization information such as you are communicating with RT(#)

            return
        
        elif (mode_code==BitArray(uint=18, length=5)):	# case 18: Transmit Last Command Word | Data Word Associated
            sendable_data_word = data_word(self.last_command_word)
            databus.add_message(sendable_data_word)
            return
        
        elif (mode_code==BitArray(uint=19, length=5)):  # case 19: Transmit Bit Word |  Data Word Associated
            
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            
            databus.add_message(sendable_status_word)
            
            sendable_data_word = data_word() #TODO: Set the paramaters of the data word
            
            return
        
        elif (mode_code==BitArray(uint=20, length=5)):	# case 20: Selected Transmitter Shutdown |  Data Word Associated
            return
        
        elif (mode_code==BitArray(uint=21, length=5)):	# case 21: Override Selected Transmitter Shutdown | Data Word Associated
            return
        
        else:				                            # default: mode_code not defined, set message error bit
            self.message_error = 1
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
                    
                    # Store copy of relevent bits
                    self.last_command_word[0:4]     = tmp_msg.rt_addr
                    self.last_command_word[5]       = tmp_msg.tx_rx
                    self.last_command_word[6:10]    = tmp_msg.sa_mode

                    # This will set the Remote Terminal's Transfer/Receiving Mode
                    if tmp_msg.tx_rx == 1:
                            # This puts the Remote Terminal in Transfer mode
                            self.rx_tx_mode == BitArray(uint=1, length=1)    
                    else:
                            # Keeps RT in Receiving mode
                            self.rx_tx_mode == BitArray(uint=0, length=1)        
                    
                    # This will process set the Subaddress Mode

                    #process_mode_code(tmp_msg.sa_mode)

                    # This will tell the Remote Terminal how many data words to send or receive

                    return

                # The RT has received a broadcast message                
                elif (tmp_msg.rt_addr.bin == BitArray(uint=31, length=5).bin):
                    ## TODO: Create case for broadcast message (ideally same as reg case, just no reply)
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

