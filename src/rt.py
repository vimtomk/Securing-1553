#!/usr/bin/env python3

from message import message, command_word, data_word, status_word
from bus import bus
from time import sleep
from bitstring import Bits, BitArray
import queue, threading, secrets
from collections import deque

class rt(object):
    
    # RT Constructor - number is to assign RT number
    def __init__(self, number):

        self.num                = BitArray(uint=number, length=5)
        self.rx_tx_mode         = "none"  # RT starts off cleared (not transmitting)
                                          # and is set for transmit mode
        self.rx_tx_mode         = BitArray(uint=0, length=1) 
        self.received_msgs      = list()  # A list of the received messages (as BitArray) used in context
                                          # to keep track of data needed for sent status words.
            
        self.instrumentation    = 0       # One bit flag, always 0 when transmitting a status word
        self.service            = 0       # Service request bit. We will not use this functionality
        self.broadcast_command  = 0       # Broadcast command bit.
        self.busy               = 0       # Busy bit. Set if the BC commands the RT not to act
        self.subsystem          = 0       # Indicates subsystem. We will not use this functionality
        self.dynamic_bus        = 0       # Set if turned into a dynamic BC.
        self.terminal           = 0       # Set if this RT has a problem. Cleared on resolution.
        self.databus            = bus()   # From now on, self.bus points to the shared data bus
        
        self.rcvd_broadcast     = 0       # Flag to indicate if RT received broadcast message for Transmit Last Status Word
        self.msg_err            = 0       # Flag to indicate if last received message from BC had an error
                                          # Condition 1 : RT receives a word with an error
                                          # Condition 2 : RT expects a stream of data words, but there is a gap
                                          # Condition 3 : RT receives a command it does not have the functionality to execute
                                          # Condition 4 : RT somehow receives the wrong number of data words
        ##TODO: create function to set last_status_word as defined in 4.3.3.5.3
        self.last_status_word   = BitArray(uint=0, length=20)   # Use to store last status word so we can transmit
        self.last_command_word  = BitArray(uint=0, length=20)   # Use to store last received command word
        self.dwords_expected    = 0       # A counter that keeps track of how many data words the terminal is still expecting to receive
        
        self.events             = deque() # A list of events (str arrays) that come from 1553_simulator

        # Start listening immediately
        #self.main()

    # Returns the Remote Terminal ID number (0-31)
    def return_rt_num(self):
        return self.num
    
    ## TODO: Generate key-pair when BC class finished
    def gen_key(self):
        return

    # Read message from bus (20 bits)
    def read_message(self):
        tmp = self.databus.read_BitArray()
        return tmp

    def read_message_timer(self, delay):
        '''Version of read_message that loops execution indefinitely and makes use of any important messages'''
        #threading.Timer(delay, self.read_message_timer, [delay]).start()
        #writeTime = 0.0 ##TODO: Figure out the time to write to the bus from current time + ~4/5 of delay???
        tmp = self.read_message()
        #print(tmp) # Debug line
        if(tmp[0] == 1 and tmp[1] == 1 and tmp[2] == 0 and (self.dwords_expected > 0)): # If a data word 110, and we are expecting a data word
            print("Data Word received by RT#!" + self.num + "\nData is: " + chr(int(tmp.bin[3:11],2)) + chr(int(tmp.bin[11:19],2)))
            self.dwords_expected = self.dwords_expected - 1
            pass
        elif((tmp.bin[3:8] == self.num.bin) or (tmp.bin[3:8] == '11111')): # If this is some other word meant for this terminal, or broadcast
            if(tmp.bin[3:8] == '11111'):
                print("This message was a broadcast!")
                pass
            if(tmp[0] == 1 and tmp[1] == 0 and tmp[2] == 1): # If a command word 101
                print("Command Word received!\nMode code is: " + tmp.bin[14:19])
                # Send the mode code to the processor function
                self.process_mode_code(BitArray('0b' + tmp.bin[14:19]))
                pass
            elif(tmp[0] == 1 and tmp[1] == 1 and tmp[2] == 1): # If a status word 111
                print("Status Word received!\nStatus was-\nError Flag: " + tmp.bin[8] + "\nService Request: " + tmp.bin[10] + "\nBusy bit: " + tmp.bin[15])
                # RT to RT communication may have this RT receive a status word from another RT
                pass
        else: # This terminal was definitely not the intended recipient of the message
            pass
        ##TODO: Add code to process the read in message (temp). This includes:
        #-Finding if the message is addressed to this device or is broadcast
        #-If this device was meant to get the message, process it
        #-If this device was meant to respond to the message, prepare a response
        ##TODO: Wherever a "pass" is in this function, there needs to be code that defines the terminal behavior in that situation...

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
            self.databus.write_BitArray(sendable_status_word)
            return 

        elif (mode_code==BitArray(uint=3, length=5)):	# case 3:  Initiate Self Test |  No Data Word Associated
            self.databus.write_BitArray(sendable_status_word)
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
            self.databus.write_BitArray(sendable_status_word)
            return
        
        elif (mode_code==BitArray(uint=7, length=5)):	# case 7:  Override Inhibit T/F bit  | No Data Word Associated
            # Override terminal flag bit FIRST
            self.terminal = 1
            # Send status word
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            self.databus.write_BitArray(sendable_status_word)
            return
        
        elif (mode_code==BitArray(uint=8, length=5)):	# case 8:  Reset Remote Terminal | No Data Word Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            self.databus.write_BitArray(sendable_status_word)
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
        


        elif (mode_code==BitArray(uint=9, length=5)):   # case 9: Receive Bus Controller Public Key | 4 Data Words Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)

            data_word_list = []           
            
            for x in range(4):

                data_word = self.read_message()
                data_word_list.append(data_word.data)
                sleep(1)

            self.BC_public_key = int(str(data_word_list[0], data_word_list[1], data_word_list[2], data_word_list[3]), 16)    
            
            return
            
            


        elif (mode_code==BitArray(uint=10, length=5)):   # case 10: Transmit Remote Terminal Public Key | 4 Data Words Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            
            sleep(1)

            self.public_key = secrets.randbelow(9223372036854775808)
            
            full_public_key = BitArray(uint= self.public_key, length=64)
            data_word_list = [full_public_key[:16], full_public_key[16:32], full_public_key[32:48], full_public_key[48:]]

            for data_word in data_word_list:
                    
                public_key_dw       =      self.create_data_word(data_word)
                self.write_message(public_key_dw)
                sleep(1)
                    
                    
          
        elif (mode_code==BitArray(uint=16, length=5)):	# case 16: Transmit Vector Word | Data Word Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            self.databus.write_BitArray(sendable_status_word)
            # Send data word containing bits 4-19 of the last command word this RT received, excluding mode code bits
            return
        
        elif (mode_code==BitArray(uint=17, length=5)):	# case 17: Synchronize (with data word) | Data Word Associated
        
        ## TODO: Create a data word with sychronization information such as you are communicating with RT(#)

            return
        
        elif (mode_code==BitArray(uint=18, length=5)):	# case 18: Transmit Last Command Word | Data Word Associated
            sendable_data_word = data_word(self.last_command_word)
            self.databus.write_BitArray(sendable_data_word)
            return
        
        elif (mode_code==BitArray(uint=19, length=5)):  # case 19: Transmit Bit Word |  Data Word Associated
            
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            
            self.databus.write_BitArray(sendable_status_word)
            
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
            if not(self.databus.is_empty()):
                tmp_msg = self.read_message()
                
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
    
    def queue_message(self, command):
        '''Takes a command in from 1553_simulator.py and turns it into an event and queues it'''
        tmp = []
        # Set dst
        if(command[0] < 10): # Pads a zero to keep string of length 4 if RT# is not double-digit
            tmp[0] = "RT0" + str(command[0])
        else:
            tmp[0] = "RT" + str(command[0])
        # Set loop flag
        if(command[1]):
            tmp[1] = "Y"
        else:
            tmp[1] = "N"
        # Set frequency
        tmp[2] = command[2]
        # Set number occurences, remember that 0 means loop infinitely!
        tmp[3] = command[3]
        # Set message string
        tmp[4] = command[4]
        # Add event to queue
        self.events.append(tmp)
    
    # RT Destructor
    def __del__(self):
        del(self)

