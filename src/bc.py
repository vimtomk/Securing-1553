#!/usr/bin/env python3

from message import message, command_word, data_word, status_word
from bus import bus
from rt import rt
from time import sleep
from bitstring import Bits, BitArray
from queue import Queue
import time, random, threading, secrets
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
        self.dead_list      = list()    # List the discarded RTs marked by an alive check

        # Instantiate commonly-used constants
        self.tx             = BitArray(uint=1, length=1)  # Tx is a logic 1
        self.rx             = BitArray(uint=0, length=1)  # Rx is a logic 0
        self.zero           = BitArray(uint=0, length=5)  # Zero in 5-bit long field
        self.thirty_one     = BitArray(uint=31, length=5) # Thirty-one is the max terminal count
        self.databus        = bus()                       # From now on, self.bus points to the shared data bus
        self.RT_keys        = {}                          # A dictionary that holds the RT keys for DHKE

        # Instantiate the queues that store events (sequences of messages to be sent)
        self.events             = deque()   # A list of events from 1553_simulator
        self.dwords_expected    = 0         # A counter that keeps track of how many data words the terminal is still expecting to receive

        # Begin normal BC behavior
        self.main()

    # Returns the terminal number of the BC
    def return_terminal_num(self):
        return self.num

    # Sends command word to the bus
    def issue_command_word(self, sendable_command_word):
        self.databus.write_BitArray(sendable_command_word)
        return

    # Sends status word to the bus
    def issue_status_word(self, sendable_status_word):
        self.databus.write_BitArray(sendable_status_word)
        return

    # Sends data word to the bus
    def issue_data_word(self, sendable_data_word):
        self.databus.write_BitArray(sendable_data_word)
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
    
    def create_status_word(self, rt_num, msg_err, instrum, serv_req, reserved,\
                           broad_comm, busy, sub_flag, dyn_bc, term_flag):
        msg_out = status_word(rt_num, msg_err, instrum, serv_req, reserved, broad_comm, busy, sub_flag, dyn_bc, term_flag)
        return msg_out

    ## TODO: finish function
    # Craft data word
    def create_data_word(self, data):
        msg_out = data_word(data)
        return msg_out

    ## TODO: Find out how to transmit command word to check on RT and then instantiate comms
    # Need to be given a specific RT to check. A Data word is
    # not required for this transfer. A Subaddress of 0 (00000) or
    # 31 (11111) imply the contents are decoded as a 5 bit command.

    ## TODO: Finish this function
    # Need to add a insert RT number into dead_list if there is no reply
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

    # Read message from bus (20 bits)
    def read_message(self):
        tmp = self.databus.read_BitArray()
        return tmp

    
    def read_message_timer(self, delay):
        '''Version of read_message that loops execution indefinitely and makes use of any important messages'''
        #threading.Timer(delay, self.read_message_timer, [delay]).start()
        #writeTime = 0.0 ##TODO: Figure out the time to write to the bus from current time + ~4/5 of delay???
        tmp = self.databus.read_BitArray()
        #print(tmp) # Debug line
        if(tmp[0] == 1 and tmp[1] == 1 and tmp[2] == 0 and (self.dwords_expected > 0)): # If a data word 110, and we are expecting a data word
            print("Data Word received by BC!\nData is: " + chr(int(tmp.bin[3:11],2)) + chr(int(tmp.bin[11:19],2)))
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
                pass
        else: # This terminal was definitely not the intended recipient of the message
            pass
        ##TODO: Add code to process the read in message (temp). This includes:
        #-Finding if the message is addressed to this device or is broadcast
        #-If this device was meant to get the message, process it
        #-If this device was meant to respond to the message, prepare a response
        ##TODO: Wherever a "pass" is in this function, there needs to be code that defines the terminal behavior in that situation...

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
    ## Bus Controller to Remote Terminal Transfer
    ## The Bus Controller sends one 16-bit receive command word
    ## immediately followed by 1 to 32 16-bit data words. 
    ## The selected Remote Terminal then sends a single 16-bit Status word.
    def BC_RT_Transfer(self, rt_num_rx, mode_code):
        tmp_msg_rx  = self.create_command_word(rt_num_rx, 0, self.zero, mode_code)
        rx_msg_sent = self.issue_command_word(tmp_msg_rx)
        for rt in self.rt_list:
            ## TODO: finish filling out create_data_word() attributes
            data_word      = self.create_data_word()
            data_word_sent = self.issue_data_word(data_word)
            return
        ## TODO: finish filling out create_status_word() attributes
        rt_status        = self.create_status_word()
        status_word_sent = self.issue_status_word(rt_status)
        return

    # RT -> BC
    ## Remote Terminal to Bus Controller Transfer
    ## The Bus Controller sends one transmit command word to a Remote Terminal. 
    ## The Remote Terminal then sends a single Status word 
    ## immediately followed by 1 to 32 words.
    def RT_BC_Transfer(self, rt_num_tx, mode_code):
        tmp_msg_tx  =   self.create_command_word(rt_num_tx, 1, self.zero, mode_code)
        self.issue_command_word(tmp_msg_tx)
        ## TODO: finish filling out create_status_word() attributes
        rt_status         = self.create_status_word()
        status_word_sent  = self.issue_status_word(rt_status)
        for rt in self.rt_list:
            ## TODO: finish filling out create_data_word() attributes
            data_word      = self.create_data_word()
            data_word_sent = self.issue_data_word(data_word)
            return
        return


    # RT -> RT
    ## Remote Terminal to Remote Terminal Transfer
    ## The Bus Controller sends out one receive command word 
    ## immediately followed by one transmit command word. 
    ## The transmitting Remote Terminal sends a Status word
    ## immediately followed by 1 to 32 data words. 
    ## The receiving Terminal then sends its Status word.
    def RT_RT_Transfer(self, rt_num_rx, rt_num_tx, mode_code):
        tmp_msg_rx  =  self.create_command_word(rt_num_rx, 0, self.zero, mode_code)
        rx_msg_sent =  self.issue_command_word(tmp_msg_rx)
        tmp_msg_tx  =  self.create_command_word(rt_num_tx, 1, self.zero, mode_code)
        tx_msg_sent =  self.issue_command_word(tmp_msg_rx)
        ## TODO: finish filling out create_status_word() attributes
        rt_status_tx         = self.create_status_word()
        tx_status_word_sent  = self.issue_status_word(rt_status_tx)
        for rt in self.rt_list:
            ## TODO: finish filling out create_data_word() attributes
            data_word      = self.create_data_word()
            data_word_sent = self.issue_data_word(data_word)
            return
        ## TODO: finish filling out create_status_word() attributes
        rt_status_rx         = self.create_status_word()
        rx_status_word_sent  = self.issue_status_word(rt_status_rx)
        return
         

    # Mode Command w/o Data Word
    ## The bus controller shall issue a transmit command to the RT using a 
    ## mode code specified in Table3-1. The RT shall, after command word 
    ## validation, transmit a status word.
    def MC_without_DW(self, rt_num, mode_code):
            tmp_msg = self.create_command_word(rt_num, 1, self.zero, mode_code)
            self.databus.write_BitArray(tmp_msg)
            # Over two seconds, look for a status word from the RT (each .25 
            # secs). If one isn't returned, assume the RT is dead.
            sleep(0.25)
            time_start = time()
            while(time() - time_start < 2):
                # Get current data of bus
                current_data = self.databus.read_BitArray()
                # If current message a status word:
                if (current_data[0:3] == BitArray(uint=7, length=3)):
                    # If current message is from the RT we were expecting 
                    # check parity bit
                    if (current_data[3:8] == BitArray(uint=rt_num, length=5)):
                        if (BitArray(uint=(current_data.count(1)) % 2 == 0, length=1) and current_data.bin[-1]):
                            return
                        else:
                            print("Parity Bit Error!")
                            return

            # Timed out, so put the RT on the dead list and return execution
            for rt in self.rt_list:
                if rt.num.uint == rt_num:
                    self.rt_list.remove(rt)
            return
                                     
            

    # Mode Command w/ Data Word Transmit
    #def MC_with_DW_TX(self):
    
    # Mode Command w/ Data Word Receive
    #def MC_with_DW_RX(self):

    
   
   
    ## A BC should first send a RT a Command Word telling it to receive, next Data Words will be sent by the BC containing BC's public key,
    ## finally a RT should send a Status Word to acknowledge that it has received the Data Words.
    def send_public_key(self):

        self.public_key = secrets.randbelow(9223372036854775808)
        self.private_key = secrets.randbelow(9223372036854775808)

        
        #Create a BitArray to be broken up into four BitArrays to transmit 
        full_public_key = BitArray(uint= self.public_key, length=64)
        data_word_list = [full_public_key[:16], full_public_key[16:32], full_public_key[32:48], full_public_key[48:]]

        for rt in self.rt_list:
            # BC create the command word telling the RT to receive four data words
            sendkeysmsg = self.create_command_word(rt, 0, 0, 9)
            
            #BC writes the Command Word to the Bus
            self.write_message(sendkeysmsg)
            sleep(1)
            
            # BC creates BitArray with its public key, creates a data word with the public key BitArray, then writes the data word to the Bus
            for data_word in data_word_list:
                public_key_dw       =      self.create_data_word(data_word)
                self.write_message(public_key_dw)
                sleep(1)

            # BC reads a word off of the Bus, it should be the Status word from the RT saying it received the public key
            rt_status_word      =     self.read_message()
            self.validate_status_word(rt_status_word)
            sleep(1)

            return
    
    
    
    
    ## A BC should first send a RT a Command Word telling it to transmit their public key, next the RT should send a status word followed by a data word containing its public key
    def receive_public_key(self):

        for rt in self.rt_list:
            # BC creates a command word telling the RT to send its public key (4 data words)

            sendmekeymsg = self.create_command_word(rt, 1, 0, 10)

            #BC writes the Command Word to the Bus
            self.write_message(sendmekeymsg)
            sleep(1)

            # An array that will hold four sixteen bit data words
            data_word_list = []
            

            # This loop grabs each data word and appends them to an array
            for x in range(4):
                rt_public_key_data   =  self.read_message()
                data_word_list.append(rt_public_key_data.data)

            #This creates a dictionary of RT public keys [rt# : rt_public_key]
            self.RT_keys[rt] = int(str(data_word_list[0] + data_word_list[1] + data_word_list[2] + data_word_list[3]), 16)   


            return


