#!/usr/bin/env python3

from message import message, command_word, data_word, status_word
from bus import bus
from rt import rt
from time import sleep
from bitstring import Bits, BitArray
from queue import Queue
import time

class bc(object):
    # BC Constructor
    def __init__(self, terminal, rts):
        # Initialize BC variables
        self.num            = BitArray(uint=terminal, length=5)     # Value indicating the terminal the bus controller is operating from
        self.received_data  = list()    # A list of the received messages used in context to keep track of data needed for received status words
        self.rt_list        = rts       # Bus controller's known RTs, pass "rts" in as a list of values from 0-30 (31 reserved for broadcast)
        self.error          = 0         # Flag to indicate if there is a communications error
        
        # Instantiate commonly-used constants
        self.tx             = BitArray(uint=1, length=1)  # Tx is a logic 1
        self.rx             = BitArray(uint=0, length=0)  # Rx is a logic 0
        self.zero           = BitArray(uint=0, length=5)  # Zero in 5-bit long field
        self.thirty_one     = BitArray(uint=31, length=5) # Thirty-one is the max terminal count
        self.bus            = bus()                       # From now on, self.bus points to the shared data bus

        # Begin normal BC behavior
        self.main()

    # Returns the terminal number of the BC
    def return_terminal_num(self):
        return self.num

    # Sends command word to the bus
    def issue_command_word(self, sendable_command_word):
        self.bus.write_BitArray(sendable_command_word)
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
            max_wait   = int(10)
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
        
        # BC -> rx_RT : (from BC) Command_word -> (from BC) Data_Word -> (from rx_BC) Status_word
        # BC -> tx_RT : (from BC) Command_word -> (from BC) Data_Word -> (from tx_BC) Status_word
        # tx_RT and rx_BT should now be sychronized to send messages between one another
        
        # TODO: Check to see if bus is empty before sending messages
        
        while(1):
            if(bus.is_empty == True):
                bus.write_BitArray(transmit_RT)
                sleep(1)
            else:
                pass
            self.bus.write_BitArray(transmit_RT_data)
            sleep(1)
            tmp_msg = self.read_message()
            
            if (int(tmp_msg.msg.bin[0:3], base=2) == 7):
                break
            else:
                    sleep(0.001)
                    continue

        while(1):
            bus.write_BitArray(receive_RT)
            sleep(1)
            bus.write_BitArray(receive_RT_data)
            sleep(1)
            tmp_msg = self.read_message()
            
            if (int(tmp_msg.msg.bin[0:3], base=2) == 7):
                break
            else:
                    sleep(0.001)
                    continue
              
        return

    # Read message from bus (20 bits)
    def read_message(self):
        tmp = self.bus.read_BitArray()
        return tmp

    # Read data bit from bus
    def read_bit(self, bit_pos):
        tmp = self.bus.read_bit(bit_pos)
        return tmp

    # Write message to bus (20 bits BitArray)
    def write_message(self, msg):
        self.bus.write_BitArray(msg)


    ## TODO: Actually figure out the logic of the bus running
    def main(self):
        pass

    # BC Destructor
    def __del__(self):
        del(self)