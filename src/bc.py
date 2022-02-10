#!/usr/bin/env python3

from message import message, command_word, data_word, status_word
from bus import bus
from rt import rt
from time import sleep
from bitstring import Bits, BitArray
from queue import Queue
import time
import random
from encryptor import DHKE
from collections import deque

class bc(object):
    # BC Constructor
    def __init__(self, terminal, rts):
        # Initialize BC variables
        self.num            = BitArray(uint=terminal, length=5)     # Value indicating the terminal the bus controller is operating from
        self.received_data  = list()    # A list of the received messages used in context to keep track of data needed for received status words
        self.rt_list        = rts       # Bus controller's known RTs, pass "rts" in as a list of values from 0-30 (31 reserved for broadcast)
        self.error          = 0         # Flag to indicate if there is a communications error
        self.init_bus       = 0         # Flag to indicate if bus has been initialised

        # Instantiate commonly-used constants
        self.tx             = BitArray(uint=1, length=1)  # Tx is a logic 1
        self.rx             = BitArray(uint=0, length=0)  # Rx is a logic 0
        self.zero           = BitArray(uint=0, length=5)  # Zero in 5-bit long field
        self.thirty_one     = BitArray(uint=31, length=5) # Thirty-one is the max terminal count
        self.databus        = bus()                       # From now on, self.bus points to the shared data bus
        self.RT_keys        = {}                          # A dictionary that holds the RT keys for DHKE

        # Instantiate the queues that store events (sequences of messages to be sent)
        self.events         = deque()                     # A list of events from 1553_simulator

        # Begin normal BC behavior
        self.main()

    # Returns the terminal number of the BC
    def return_terminal_num(self):
        return self.num

    # Sends command word to the bus
    def issue_command_word(self, sendable_command_word):
        self.databus.write_BitArray(sendable_command_word)
        return

    # Validates that a received status word has no errors
    def validate_status_word(self, status_word):
        if (status_word.msg_type_bits !=  "111"):
            self.error = 1
        # Check for odd parity
        elif ( (status_word.count(1) % 2) == 0):
            self.error = 1
        return self.error

    # Validates that a received data word has no errors
    def validate_data_word(self, data_word):
        if (data_word.msg_type_bits !=  "101"):
            self.error = 1
        # Check for odd parity
        elif ( (data_word.count(1) % 2) == 0):
            self.error = 1
        return self.error
        
    # Define other functions of a BC here
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

    ## TODO: finish function
    # Craft command word
    def create_command_word(self, target_rt_addr, txrx, sa_mode, dw_count):
        msg_out = command_word(target_rt_addr, txrx, sa_mode, dw_count)
        return msg_out
    
    ## TODO: finish function
    # Craft data word
    def create_data_word(self, data):
        msg_out = data_word(data)
        return msg_out

    ## TODO: Find out how to transmit command word to check on RT and then instantiate comms (reading now)
    
    ## TODO: Finish this function
    # For each rt on the bus, create a command word one at a time and wait for response (status check)
    def check_rts(self):
        
        for rt in self.rt_list:
            # The two at the end ensures we are using mode code 2 which means the BC wants the RT to send a status word
            self.create_command_word(rt, 1, 0, 2)
            # Now wait a second and listen for message on bus
            sleep(1)
            # Wait no longer than 10 seconds
            max_wait   = int(1)
            start_time = time.time()
            while (time.time() - start_time) < max_wait:
                # Get most first message on the bus (front of queue)
                tmp_msg = self.read_message()
                
                # Check if message is type Status Word
                if (int(tmp_msg.msg.bin[0:3], base=2) == 7):
                    # Check if status word from correct RT
                    if (int(tmp_msg.msg.bin[3:8], base=2) == rt):
                        # If no parity error, then process message
                        if (tmp_msg.msg.check_err()):
                            return
                        
                        ## TODO: Check if we can do that
                        # If there is a parity error, may want RT to resend
                        else:
                            print("Parity error!")
                            return
                        return

                # If message is not status word, wait a min and continue
                else:
                    sleep(0.001)
                    continue
            
        return

    ## TODO: Finish this function
    # Creates a message block that syhcronizes RTs to communicate
    def synchronize(self, tx_RT, rx_RT):

        #One RT must be set to send while the other must be set to transmit 
        transmit_RT     =   self.create_command_word(tx_RT, 1, 0, 17)
        receive_RT      =   self.create_command_word(rx_RT, 0, 0, 17)
        
        # The command words should be followed with a data word that tells the RT
        # the specific RT it needs to sychronize with
        transmit_RT_data = self.create_data_word(rx_RT) # Should include the RT number that is receiving
        receive_RT_data = self.create_data_word(tx_RT)  # Should include the RT number that is transmitting
        
        # 1. BC -> rx_RT : (from BC) Command_word -> (from BC) Data_Word -> (from rx_BC) Status_word
        # 2. BC -> tx_RT : (from BC) Command_word -> (from BC) Data_Word -> (from tx_BC) Status_word
        # tx_RT and rx_BT should now be sychronized to send messages between one another
        
      
        # This while loop executes step (1) above
        while(1):
            if(self.databus.is_empty == True):
                self.write_message(transmit_RT) # Command Word
                sleep(0.5)
            else:
                sleep(0.5)
                continue

            if(self.databus.is_empty == True):

                self.write_message(transmit_RT_data) # Data Word
                sleep(0.5)
            else:
                sleep(0.5)
                continue

            tmp_msg = self.read_message() # Read Status Word from Bus
            
            if (int(tmp_msg.msg.bin[0:3], base=2) == 7):
                break
            else:
                sleep(0.5)
                continue

        # This while loop executes step (2) above
        while(1):
            
            if (self.databus.is_empty == True):
                self.write_message(receive_RT) # Command Word
                sleep(0.5)
            else:
                sleep(0.5)
                continue
            
            if (self.databus.is_empty == True):
                self.write_message(receive_RT_data) # Data Word
                sleep(0.5)
            else:
                sleep(0.5)
                continue
            
            tmp_msg = self.read_message() # Read Status Word from Bus
            
            if (int(tmp_msg.msg.bin[0:3], base=2) == 7):
                break
            else:
                sleep(0.5)
                continue
              
        return

    # Read message from bus (20 bits)
    def read_message(self):
        tmp = self.databus.read_BitArray()
        return tmp

    # Read data bit from bus
    def read_bit(self, bit_pos):
        tmp = self.databus.read_bit(bit_pos)
        return tmp

    # Write message to bus (20 bits BitArray)
    def write_message(self, msg):
        self.databus.write_BitArray(msg)


    ## TODO: Actually figure out the logic of the bus running
    def main(self):
        pass

    # BC Destructor
    def __del__(self):
        del(self)

    ## TODO: Create functions for the optional broadcast transfers between BC and Specific RT's or Pair of RT's

    # BC -> RT
    def BC_RT_Transfer(self, rx_RT):
        receive_RT      =   self.create_command_word(rx_RT, 0, 0, 17)
        for rt in self.rt_list:
            # send data words
            return
        #selected RT sends status word
        return

    # RT -> BC
    #def RT_BC_Transfer(self):

    # RT -> RT
    #def RT_RT_Transfer(self):

    # Mode Command w/o Data Word
    #def MC_without_DW(self):

    # Mode Command w/ Data Word Transmit
    #def MC_with_DW_TX(self):
    
    # Mode Command w/ Data Word Receive
    #def MC_with_DW_RX(self):

    

    ## TODO: Create a function for sending keys for sending BC's public key to each RT
    ## A BC should first send a RT a Command Word telling it to receive, next Data Words will be sent by the BC containing BC's public key,
    ## finally a RT should send a Status Word to acknowledge that it has received the Data Words.

    def send_public_key(self):

        self.public_key = random.randint(1,65000)
        self.private_key = random.randint(1,65000)

        

        for rt in self.rt_list:
            # BC create the command word telling the RT to receive two data words
            sendkeysmsg = self.create_command_word(rt, 0, 0, 2)
            
            #BC writes the Command Word to the Bus
            self.write_message(sendkeysmsg)
            sleep(1)
            
            
            while i < (sendkeysmsg.mode_code):
                
                # We need to break up the public key into two bytes so that one byte can be sent in each message preceeded by the message number
                hex_byte_1 = hex(self.public_key)[4:]
                hex_byte_2 = hex(self.public_key)[2:4]
                
                
                
                #data_word = self.create_data_word()

                


                i = i + 1
                    
                

        


    


        pass