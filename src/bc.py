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
from math import ceil

class bc(object):
    # BC Constructor
    def __init__(self, terminal, rt_array=[]):

        # Initialize BC variables
        self.num            = BitArray(uint=terminal, length=5)     # Value indicating the terminal the bus controller is operating from
        self.received_data  = list()    # A list of the received messages used in context to keep track of data needed for received status words
        self.rt_list        = rt_array  # Bus controller's known RTs, pass "rts" in as a list of values from 0-30 (31 reserved for broadcast)
        self.error          = 0         # Flag to indicate if there is a communications error
        self.init_bus       = 0         # Flag to indicate if bus has been initialised
        self.dead_list      = list()    # List the discarded RTs marked by an alive check
        self.frequency      = 1         # Set the frequency at which to send the messages on the bus

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
        self.dwords_stored      = ""        # Stores a string of data words as they come in, eventually being output to the terminal.

        # Flags for handling execution of message transfers
        self.read_permission    = True      # Keeps track of if the BC is O.K. to read from the bus
        self.write_permission   = False     # Keeps track of if the BC is the one who should be writing to the bus this cycle

        self.public_key         = None      # Initialized to none type because it is initialized when a function is called
        self.private_key        = None      # Initialized to none type because it is initialized when a function is called

        # For Timer functions, create a variable to check if the BC object still exists before looping execution
        self.exists = "Yes!"


    def main(self):

    
        # Loop the execution of BC frequently, and let it orchestrate bus communications
        if(self.exists == "Yes!"): 
            
            # If the BC has been removed, stop execution
            # Handle events in the event list if the databus free to be use
            if (not(self.databus.is_in_use()) and self.write_permission == True):
                self.event_handler()

        print("Exit main lol")
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
        self.error = 0
        if (status_word.bin[0:3] !=  "111"):
            self.error = 1
        # Check for odd parity in the 16 data bits (exclude the type bits)
        elif ((status_word.raw_data.count(1) % 2) == 0):
            self.error = 1
        return self.error

    # Validates that a received data word has no errors
    def validate_data_word(self, data_word):
        self.error = 0
        if (data_word.msg_type_bits !=  "101"):
            self.error = 1
        # Check for odd parity
        elif ( (data_word.raw_data.count(1) % 2) == 0):
            self.error = 1
        return self.error
        
    # Define other functions of a BC here
    def queue_message(self, command):
        '''Takes a command in from 1553_simulator.py and turns it into an event/s and adds it/them to the back of the queue'''
        self.events.append(command)
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

    # For each rt on the bus, create a command word one at a time and wait for response (status check)
    def check_rts(self):
        
        for rt in self.rt_list:
            # The two at the end ensures we are using mode code 2 which means the BC wants the RT to send a status word
            self.create_command_word(rt, self.tx, self.zero, 2)
            # Now wait a second and listen for message on bus
            sleep(self.frequency)
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
                        if(tmp_msg.count(1) % 2 == 0):
                            # Parity Error
                            print("Parity error!")
                            pass
                        # If there is a parity error, may want RT to resend
                        else:
                            # No Parity Error
                            pass

                # If message is not status word, wait a min and continue
                else:
                    sleep(0.001)
                    continue
            # insert RT number into dead_list if there is no reply
            else:
                self.rt_list.remove(rt)
        return

    # Read message from bus (20 bits)
    def read_message(self):
        tmp = self.databus.read_BitArray()
        return tmp

    
    def read_message_timer(self, delay):
        '''Version of read_message that loops execution indefinitely and makes use of any important messages'''
        #if(self.exists == "Yes!"):
        #   threading.Timer(delay, self.read_message_timer, [delay]).start()
        #   writeTime = float(delay) - (float(delay)/float(5)) # Time near the end of cycle where the terminal should write if it needs to
        #   threading.Timer(writeTime, self.write_message_timer).start()
        #else:
        #   return
        tmp = self.read_message()
        #print(tmp) # Debug line
        if(tmp[0] == 1 and tmp[1] == 1 and tmp[2] == 0 and (self.dwords_expected > 0)): # If a data word 110, and we are expecting a data word
            print("Data Word received by BC!\nData is: " + chr(int(tmp.bin[3:11],2)) + chr(int(tmp.bin[11:19],2)))
            if(self.dwords_expected != 0):
                self.dwords_expected = self.dwords_expected - 1
            else: # This terminal is not expecting data words. Stop reading.
                return
            self.dwords_stored.append(chr(int(tmp.bin[3:11],2)) + chr(int(tmp.bin[11:19],2)))
            if(self.dwords_expected == 0):
                print(self.dwords_stored)
                self.dwords_stored = ""
            if(tmp.count(1) % 2 == 0): # Failed parity check
                self.error = 1
            #else: # Passed parity check
        elif((tmp.bin[3:8] == self.num.bin) or (tmp.bin[3:8] == '11111')): # If this is some other word meant for this terminal, or broadcast
            if(tmp.bin[3:8] == '11111'):
                print("This message was a broadcast!")
            if(tmp[0] == 1 and tmp[1] == 0 and tmp[2] == 1): # If a command word 101
                # Check to see if the command word contains a Mode Code or a Word Count
                if((tmp[9:14] == "00000") or tmp[9:14] == "11111"): # If subaddress field is either of these, it is a mode code in the next 5-bit field
                    print("Command Word received!\nMode code is: " + tmp.bin[14:19])
                    # Send the mode code to the processor function
                    self.process_mode_code(BitArray('0b' + tmp.bin[14:19]))
                #else: # This command word is permitting the terminal to send data words. The BC should not be receiving these types of messages!
            if(tmp.count(1) % 2 == 0): # Failed parity check
                self.error = 1
            #else: # Passed parity check
            elif(tmp[0] == 1 and tmp[1] == 1 and tmp[2] == 1): # If a status word 111
                print("Status Word received!\nStatus was-\nError Flag: " + tmp.bin[8] + "\nService Request: " + tmp.bin[10] + "\nBusy bit: " + tmp.bin[15])
                if(tmp.count(1) % 2 == 0): # Failed parity check
                    self.error = 1
            #else: # Passed parity check
        #else: # This terminal was definitely not the intended recipient of the message

    def write_message_timer(self):
        '''At the end of a time interval, this function is called and if the terminal has a need and the permissions
        to write to the bus, it will do so.'''
        if((self.write_permission == False) or (len(self.events) == 0)): # If there is no permission to write anything or nothing to write, return immediately.
            return
        print("Writing a message to the bus!")
        #self.databus.write_BitArray(self.event_to_word(self.events.pop()))
        return

    # Read data bit from bus
    def read_bit(self, bit_pos):
        tmp = self.databus.read_bit(bit_pos)
        return tmp

    # Write message to bus (20 bits BitArray)
    def write_message(self, msg):
        self.databus.write_BitArray(msg)

    # Function to wait on write permissions to continue execution.
    def wait_for_write_perm(self):
        while(not(self.write_permission)):
            sleep(0.01)
            pass
        return

    # Function to wait on read permissions to continue execution.
    def wait_for_read_perm(self):
        while(not(self.read_permission)):
            sleep(0.01)
            pass
        return

    # BC Destructor
    def __del__(self):
        self.exists = "No."
        del(self)

    # Event Handler
    def event_handler(self):
        print("event handling")
        if(len(self.events) > 0):
            # Remove leftmost (oldest) item in events deque and put it in temp var
            event = self.events.popleft()
            
            # If event is supposed to repeat, do this
            if (int(event[2]) == 1):
                # Decrement the num occurences if num occurences > 0 and not inf (-1), put back on right of events list 
                if (int(event[4]) > 0):
                    event[4] = str(int(event[4]) - 1)
                    self.events.append(event)
                
                elif (int(event[4]) == -1):
                    self.events.append(event)
            
            # Wait until bus is not in use before continuing (checking each 5 ms)
            while (self.databus.is_in_use == 1):
                sleep(0.005)
                pass

            # Set databus as being in use
            self.databus.set_in_use(1)
            self.write_permission = True


            # BC -> RT
            if (event[0][:2] == "BC" and event[1][:2] == "RT" and self.write_permission == True):
                print("BC to RT transfer!")
                # Do the BC->RT transfer
                self.BC_RT_Transfer(int(event[1][-2:]), event[6])
                self.databus.set_in_use(0)
                return

            # RT -> BC
            elif (event[0][:2] == "RT" and event[1][:2] == "BC"):
                print("RT to BC transfer!")
                # Do the RT->BC transfer
                self.RT_BC_Transfer(int(event[1][-2:]), event[6])
                return

            # RT -> RT
            elif (event[0][:2] == "RT" and event[1][:2] == "RT"):
                print("RT to RT transfer!")
                # Do the RT->RT transfer
                self.RT_RT_Transfer(int(event[1][-2:]), int(event[0][-2:]), event[6])
                return

            # Otherwise, undefined transfer
            else: 
                print("Event undefined transfer! ", event[0], "->", event[1])
                return
        
        # No more events, therefore ~~exit~~ pass
        else:
            #exit()
            pass

    ## TODO: Finish adding logic for waiting on write perms to the bus

    # BC -> RT
    ## Bus Controller to Remote Terminal Transfer
    ## The Bus Controller sends one 16-bit receive command word
    ## immediately followed by 1 to 32 16-bit data words. 
    ## The selected Remote Terminal then sends a single 16-bit Status word.
    def BC_RT_Transfer(self, rt_num_rx, data):

        # Creates an array of two characters that will later be turning into 16 bit data words
        array = self.string_to_tokens(data)

        # Creates a message count to pass to the create command word function to tell the RT how many words to rx
        msg_count = len(array)

        bit_string_list = []

        # Create list of bit strings
        for strn in array:
            bs  = Bits('0b'+(''.join(format(i, '08b') for i in bytearray(strn, encoding='utf-8'))))
            bit_string_list.append(bs)     

        
        # Create and issue the command word for the receiving RT
        tmp_msg_rx     =    self.create_command_word(rt_num_rx, self.rx, self.zero, msg_count)
        self.issue_command_word(tmp_msg_rx)
        (self.rt_list[self.rt_list.index(rt_num_rx)]).read_permission = True
        self.write_permisison = False
        # Set the designated rt's write permission to True and wait to be given back write perms
        (self.rt_list[self.rt_list.index(rt_num_rx)]).write_permission = True
        self.wait_for_write_perm()
        
        # Create and issue 1 to 32 16-bit data words
        for bs in bit_string_list:
            ## TODO: Get a better timer system b/w BC and RT
            sleep(self.frequency)
            data_msg     =    self.create_data_word(bs)
            self.issue_data_word(data_msg)
            
        
        # Create and issue the status word from the receiving RT
        rt_status_word      =    self.read_message()
        
        if (self.validate_status_word(rt_status_word) == 0):
            print("RT has successfully received the message from BC.")
            self.error = 0
        else:
            print("***STATUS MESSAGE ERROR***")
            self.error = 1
            return
        
        # Unset the BC write permission when done
        #self.write_permission =False
        print("The transfer from BC to RT " + rt_num_rx + " has terminated.")
        return

    # RT -> BC
    ## Remote Terminal to Bus Controller Transfer
    ## The Bus Controller sends one transmit command word to a Remote Terminal. 
    ## The Remote Terminal then sends a single Status word 
    ## immediately followed by 1 to 32 words.
    def RT_BC_Transfer(self, rt_num_tx, data):
        
        # Creates an array of two characters that will later be turning into 16 bit data words
        array = self.string_to_tokens(data)

        # Creates a message count to pass to the create command word function to tell the RT how many words to send
        msg_count = len(array)     
        
        # Create and issue the command word for the transmitting RT
        tmp_msg_tx     =    self.create_command_word(rt_num_tx, self.tx, self.zero, msg_count)
        self.issue_command_word(tmp_msg_tx)
        self.write_permission = False
        (self.rt_list[self.rt_list.index(rt_num_tx)]).write_permission = True
        
        # Waits for a status word to be received from the transmitting RT and validate it
        
        rt_status_word =    self.read_message()
        sleep(self.frequency)
        
        if (self.validate_status_word(rt_status_word) == 0):
            print("RT " + rt_num_tx + " is sending messages to BC")
            self.error = 0
        else:
            print("***STATUS MESSAGE ERROR***")
            self.error = 1
            return
        
        # Receive messages from the transmitting RT and decode the data words back into a message
        data_word_list = []

        for msg in range(0,msg_count):
                msg = self.read_message()
                char1 = chr(int(msg[0:8], 2))
                char2 = chr(int(msg[8:], 2))
                data_word_list.append(char1 + char2)
                sleep(self.frequency)

        for i in data_word_list:
                message += i

        print("The message received from " + rt_num_tx + " is " + message)
        self.wait_for_write_perm()
        return ("The transfer from RT " + rt_num_tx + " to BC has terminated")

    ## TODO: Fix once RT-RT timing is finished
    # RT -> RT
    ## Remote Terminal to Remote Terminal Transfer
    ## The Bus Controller sends out one receive command word 
    ## immediately followed by one transmit command word. 
    ## The transmitting Remote Terminal sends a Status word
    ## immediately followed by 1 to 32 data words. 
    ## The receiving Terminal then sends its Status word.
    def RT_RT_Transfer(self, rt_num_rx, rt_num_tx, data):
        
        # Creates an array of two characters that will later be turning into 16 bit data words
        array = self.string_to_tokens()

        # Creates a message count to pass to the create command word function to tell the RT how many words to send
        msg_count = len(array)

        # Create and issue the command word for the receiving RT
        tmp_msg_rx    =  self.create_command_word(rt_num_rx, self.rx, self.zero, msg_count)
        self.issue_command_word(tmp_msg_rx)
        sleep(self.frequency)
        
        # Create and issue the command word for the transmitting RT
        tmp_msg_tx    =  self.create_command_word(rt_num_tx, self.tx, self.zero, msg_count)
        self.issue_command_word(tmp_msg_tx)
        sleep(self.frequency)
        
        # Wait for transmitting RT to send a status word back and validate the status word
        rt_status_tx  = self.read_message()
        sleep(self.frequency)
        
        if (self.validate_status_word(rt_status_tx) == 0):
            print("RT " + rt_num_tx + " is sending messages to RT " + rt_num_rx + ".")
            self.error = 0
        else:
            print("***STATUS MESSAGE ERROR***")
            self.error = 1
            return

         
        # Create and issue the status word from the receiving RT
        rt_status_rx  = self.read_message()
        sleep(self.frequency)
        
        if (self.validate_status_word(rt_status_rx) == 0):
            print("RT " + rt_num_rx + " is finished receiving messages from RT " + rt_num_tx + ".")
            self.error = 0
        else:
            print("***STATUS MESSAGE ERROR***")
            self.error = 1
            return
        
        return
         

    # Mode Command w/o Data Word
    ## The bus controller shall issue a transmit command to the RT using a 
    ## mode code specified in Table3-1. The RT shall, after command word 
    ## validation, transmit a status word.
    def MC_without_DW(self, rt_num, mode_code):
            tmp_msg = self.create_command_word(rt_num, self.tx, self.zero, mode_code)
            
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

    def MC_with_DW_TX(self,  rt_num,  msg_count):
            
            tmp_msg = self.create_command_word(rt_num,  self.tx,  self.zero,  msg_count)
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
                print("Not all messages were received.")
            
    # Mode Command w/ Data Word Receive
    # The bus controller shall issue a receive command word to the RT using a 
    # mode code specified in Table3-1. The mode code will be (9, 16-21) The RT shall, after a command 
    # word validation, receive status word, then receive data word(s).
    def MC_with_DW_RX(self, rt_num, data, msg_count):
        tmp_msg = self.create_command_word(rt_num,   self.rx,   self.zero,  msg_count)
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
        full_public_key = BitArray(uint=self.public_key, length=64)
        data_word_list = [full_public_key[:16], full_public_key[16:32], full_public_key[32:48], full_public_key[48:]]

        for rt in self.rt_list:
            # BC create the command word telling the RT to receive four data words
            sendkeysmsg = self.create_command_word(rt, 0, 0, 9)
            
            #BC writes the Command Word to the Bus
            self.write_message(sendkeysmsg)
            sleep(self.frequency)
            
            public_key_dw = data_word()
            # BC creates BitArray with its public key, creates a data word with the public key BitArray, then writes the data word to the Bus
            for d_word in data_word_list:
                tmp_msg = public_key_dw.create_data_word(d_word)
                self.write_message(tmp_msg)
                sleep(self.frequency)

            # BC reads a word off of the Bus, it should be the Status word from the RT saying it received the public key
            rt_status_word      =     self.read_message()
            self.validate_status_word(rt_status_word)
            sleep(self.frequency)

            return
    
    
    ## A BC should first send a RT a Command Word telling it to transmit their public key, next the RT should send a status word followed by a data word containing its public key
    def receive_public_key(self):

        for rt in self.rt_list:
            
            # BC creates a command word telling the RT to send its public key (4 data words)
            sendmekeymsg = self.create_command_word(rt, 1, 0, 10)

            #BC writes the Command Word to the Bus
            self.write_message(sendmekeymsg)
            sleep(self.frequency)


            # BC reads a word off of the Bus, it should be the Status word from the RT saying it is transmitting its public key
            rt_status_word      =     self.read_message()
            self.validate_status_word(rt_status_word)
            sleep(self.frequency) 


            # An array that will hold four sixteen bit data words
            data_word_list = []
            

            # This loop grabs each data word and appends them to an array
            for x in range(4):
                rt_public_key_data   =  self.read_message()
                data_word_list.append(rt_public_key_data[4:])

            #This creates a dictionary of RT public keys [rt# : rt_public_key]
            self.RT_keys[rt] = int(str(data_word_list[0] + data_word_list[1] + data_word_list[2] + data_word_list[3]), 16)

              


            return
    
    def string_to_tokens(in_string):
        '''Takes in a string and returns a list of 2-character pairs from that string.
        If the string's length is not divisible by 2, the final character is accompanied by a space.'''
        out_tokens = []
        i = int(len(in_string)/2)
        if(len(in_string) % 2):
            # String length is odd. A space needs to be padded at the end.
            i = i + 1
        for j in range(0,i):
            if(len(in_string[2 * j:]) == 1):
                out_tokens.append( in_string[2 * j] + " " )
            else:
                out_tokens.append( in_string[2 * j] + in_string[2 * j + 1])
        return out_tokens