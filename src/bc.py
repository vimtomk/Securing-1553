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
        self.events             = deque()   # A list of events from 1553_simulator. Add critical messages (like responses to other devices) to the front of the queue
        self.dwords_expected    = 0         # A counter that keeps track of how many data words the terminal is still expecting to receive
        self.write_permission   = False     # Keeps track of if the BC is the one who should be writing to the bus this cycle

        # Begin normal BC behavior
        self.main()
        return

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
        '''Takes a command in from 1553_simulator.py and turns it into an event/s and adds it/them to the back of the queue'''
        #TODO: Re-write / modify this function to correctly handle queueing events given the new requirements and format of inputs
        pass
        '''# Determine how many character pairs there will be, and therefore how many data words need to be queued
        number_of_pairs = int(len(command[4])/2)
        if ((len(command[4]) % 2) == 1):
            number_of_pairs = number_of_pairs + 1
        # Take string and parse it into an array of two-character tokens
        char_pairs = []
        for x in range(0, number_of_pairs, 2):
            char_pairs.append(command[4][x:(x+2)])
        for char_pair in char_pairs:
            if(len(char_pair) == 1):
                char_pair = char_pair + " "
            tmp = []
            # Set dst
            tmp[0]  = "d" # Indicate that this event is to send a data word
            if(command[0] < 10): # Pads a zero to keep string of length 4 if RT# is not double-digit
                tmp[1] = "RT0" + str(command[0])
            else:
                tmp[1] = "RT" + str(command[0])
            # Set loop flag
            if(command[1]):
                tmp[2] = "Y"
            else:
                tmp[2] = "N"
            # Set frequency
            tmp[3] = command[2]
            # Set number occurences, remember that 0 means loop infinitely!
            tmp[4] = command[3]
            # Set 16 bits of message data
            tmp[5] = BitArray("0b" + bin(ord(char_pair[0]))[2:] + bin(ord(char_pair[0]))[2:])
            # Add event to queue
            self.events.append(tmp)'''
        return
    
    # Takes an event from the queue and turns it into an acutal sendable message
    ##TODO: Flesh out this function to translate events for command and status words
    def event_to_word(self, event):
        '''Takes an event and returns an actual 20-bit BitArray message corresponding to that event'''
        if event[0] == "d": # This event is for a data word
            if(event[2] == "Y"):
                if(event[4] == 0):
                    # Message repeats indefinitely, just add a copy to the queue
                    threading.Timer(event[3], self.events.append, [event]).start()
                elif(event[4] > 1):
                    # Decrement number of messages remaining, and add next event to queue
                    event[4] = event[4] - 1
                    threading.Timer(event[3], self.events.append, [event]).start()
            return self.create_data_word(int(event[5].bin, 2))
        elif event[0] == "c": # This event is for a command word
            ##TODO: Define how an event for a command word is coded
            pass
        elif event[0] == "s": # This event is for a status word
            return self.create_status_word(self.num, self.error, 0, 0)
        #BitArray(uint=int(event[0][2:5]), length=5)
        return

    # Craft command word
    def create_command_word(self, target_rt_addr, txrx, sa_mode, dw_count):
        msg_out = command_word.create_command_word(target_rt_addr, txrx, sa_mode, dw_count)
        return msg_out
    
    # Craft status word
    def create_status_word(self, rt_num, msg_err, broad_comm, dyn_bc):
        msg_out = status_word.create_status_word(rt_num, msg_err, 0, 0, 0, broad_comm, 0, 0, dyn_bc, 0)
        return msg_out

    # Craft data word
    def create_data_word(self, data):
        msg_out = data_word.create_data_word(data)
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
        writeTime = float(delay) - (float(delay)/float(5)) # Time near the end of cycle where the terminal should write if it needs to
        #threading.Timer(writeTime, self.write_message_timer).start()
        tmp = self.read_message()
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

    def write_message_timer(self):
        '''At the end of a time interval, this function is called and if the terminal has a need and the permissions
        to write to the bus, it will do so.'''
        if((self.write_permission == False) or (len(self.events) == 0)): # If there is no permission to write anything or nothing to write, return immediately.
            return
        self.databus.write_BitArray(self.event_to_word(self.events.pop()))
        return

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
    def BC_RT_Transfer(self, rt_num_rx, msg_count, data):
        # Create and issue the command word for the receiving RT
        tmp_msg_rx     = self.create_command_word(rt_num_rx, 0, self.zero, msg_count)
        self.issue_command_word(tmp_msg_rx)
        # Create and issue 1 to 32 16-bit data words
        for rt in self.rt_list:
            data_word  = self.create_data_word(data)
            self.issue_data_word(data_word)
            return
        # Create and issue the status word from the receiving RT
        rt_status      = self.create_status_word(rt_num_rx, rt_num_rx.msg_err, rt_num_rx.rcvd_broadcast, rt_num_rx.dynamic_bus)
        self.issue_status_word(rt_status)
        return

    # RT -> BC
    ## Remote Terminal to Bus Controller Transfer
    ## The Bus Controller sends one transmit command word to a Remote Terminal. 
    ## The Remote Terminal then sends a single Status word 
    ## immediately followed by 1 to 32 words.
    def RT_BC_Transfer(self, rt_num_tx, msg_count, data):
        # Create and issue the command word for the transmitting RT
        tmp_msg_tx     =  self.create_command_word(rt_num_tx, 1, self.zero, msg_count)
        self.issue_command_word(tmp_msg_tx)
        # Create and issue the status word from the transmitting RT
        rt_status      =  self.create_status_word(rt_num_tx, rt_num_tx.msg_err, rt_num_tx.rcvd_broadcast, rt_num_tx.dynamic_bus)
        self.issue_status_word(rt_status)
        # Create and issue 1 to 32 16-bit data words
        for rt in self.rt_list:
            data_word  = self.create_data_word(data)
            self.issue_data_word(data_word)
            return
        return


    # RT -> RT
    ## Remote Terminal to Remote Terminal Transfer
    ## The Bus Controller sends out one receive command word 
    ## immediately followed by one transmit command word. 
    ## The transmitting Remote Terminal sends a Status word
    ## immediately followed by 1 to 32 data words. 
    ## The receiving Terminal then sends its Status word.
    def RT_RT_Transfer(self, rt_num_rx, rt_num_tx, msg_count, data):
        # Create and issue the command word for the receiving RT
        tmp_msg_rx    =  self.create_command_word(rt_num_rx, 0, self.zero, msg_count)
        self.issue_command_word(tmp_msg_rx)
        # Create and issue the command word for the transmitting RT
        tmp_msg_tx    =  self.create_command_word(rt_num_tx, 1, self.zero, msg_count)
        self.issue_command_word(tmp_msg_rx)
        # Create and issue the status word from the transmitting RT
        rt_status_tx  = self.create_status_word(rt_num_tx, rt_num_tx.msg_err, rt_num_tx.rcvd_broadcast, rt_num_tx.dynamic_bus)
        self.issue_status_word(rt_status_tx)
        # Create and issue 1 to 32 16-bit data words
        for rt in self.rt_list:
            data_word = self.create_data_word(data)
            self.issue_data_word(data_word)
            return
        # Create and issue the status word from the receiving RT
        rt_status_rx  = self.create_status_word(rt_num_rx, rt_num_rx.msg_err, rt_num_rx.rcvd_broadcast, rt_num_rx.dynamic_bus)
        self.issue_status_word(rt_status_rx)
        return
         

    # Mode Command w/o Data Word
    ## The bus controller shall issue a transmit command to the RT using a 
    ## mode code specified in Table3-1. The RT shall, after command word 
    ## validation, transmit a status word.
    def MC_without_DW(self, rt_num, mode_code):
            tmp_msg = self.create_command_word(rt_num, 1, self.zero, mode_code)
            ##TODO: Use Julien's function
            self.databus.write_BitArray(tmp_msg)
            # Over two seconds, look for a status word from the RT (each .25 
            # secs). If one isn't returned, assume the RT is dead.
            sleep(0.25)
            #self.read_message_timer(1)
            time_start = time()
            while(time() - time_start < 2):
                # Get current data of bus
                current_data = self.read_message()
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
    # The bus controller shall issue a transmit command word to the RT using a 
    # mode code specified in Table3-1. The mode code will be (10, 16-21) The RT shall, after a command 
    # word validation, transmit status word, then transmit data word(s).

    def MC_with_DW_TX(self, rt_num, msg_count):
            tmp_msg = self.create_command_word(rt_num, 1, self.zero, msg_count)
            self.databus.write_BitArray(tmp_msg)
            # Over two seconds, look for a status word from the RT (each .25
            # secs). If one isn't returned, assume the RT is dead.
            sleep(0.25)
            time_start = time()
            while(time() - time_start < 2):
                # Get current data of bus
                current_data = self.read_message()
                # If current message is a status word:
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

            # The BC at this point has successively received a status word from the RT and should now check for
            # data words to be received.
            for msg in msg_count:
                msg = self.read_message()
                
                # If the word from the bus is a data word append the message to the received data list 
                if (current_data[0:3] == BitArray(uint=6, length=3)):
                    self.received_data.append(msg)
                    
            if (len(self.received_data) != msg_count):
                print("Not all messages were received")
            

            


    # Mode Command w/ Data Word Receive
    # The bus controller shall issue a receive command word to the RT using a 
    # mode code specified in Table3-1. The mode code will be (9, 16-21) The RT shall, after a command 
    # word validation, receive status word, then receive data word(s).
    def MC_with_DW_RX(self, rt_num, data, msg_count):
        tmp_msg = self.create_command_word(rt_num, 0, self.zero, msg_count)
        self.databus.write_BitArray(tmp_msg)
        # Over two seconds, look for a status word from the RT (each .25
        # secs). If one isn't returned, assume the RT is dead.
        sleep(0.25)
        time_start = time()
        while(time() - time_start < 2):
            # Get current data of bus
            current_data = self.read_message()
            # If current message is a status word:
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

            # The BC should write all messages to the RT
            for msg in msg_count:
                
                tmp_msg = self.create_data_word(data)
                self.databus.write_BitArray(tmp_msg)












        
    
   
   
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