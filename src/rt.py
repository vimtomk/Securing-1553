#!/usr/bin/env python3

from message import message, command_word, data_word, status_word
from bus import bus
from time import sleep
from bitstring import Bits, BitArray
import queue, threading, secrets
from collections import deque
import sys

#from src.test import decrypt

class rt(object):
    
    # RT Constructor - number is to assign RT number
    def __init__(self, number, crypt=False, key=None):

        self.num                = BitArray(uint=number, length=5)
        self.rx_tx_mode         = BitArray(uint=0, length=1) # RT starts off cleared and is set for transmit mode
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
        self.encrypted          = crypt   # Denotes if this RT should use encryption in RT->RT Transfers
        self.shift              = key     # The shift to be used for the Caesar Cipher

        self.rcvd_broadcast     = 0       # Flag to indicate if RT received broadcast message for Transmit Last Status Word
        self.msg_err            = 0       # Flag to indicate if last received message from BC had an error
                                          # Condition 1 : RT receives a word with an error (parity)
                                          # Condition 2 : RT expects a stream of data words, but there is a gap (a cycle is missed getting the next data word)
                                          # Condition 3 : RT receives a command it does not have the functionality to execute (unimplemented mode code)
                                          # Condition 4 : RT somehow receives the wrong number of data words (missing data words, extra data words)
        
        self.last_status_word   = BitArray(uint=0, length=20)   # Use to store last status word so we can transmit
        self.last_command_word  = BitArray(uint=0, length=20)   # Use to store last received command word
        self.dwords_expected    = 0       # A counter that keeps track of how many data words the terminal is still expecting to receive
        self.dwords_stored      = []      # Stores a list of data words as they come in, eventually being output to the terminal.

        # Flags for handling execution of message transfers
        self.num_reads          = 0       # Count indicating how many data words this RT has to read from the bus in a given transfer
        self.num_writes         = 0       # Count indicating how many data words this RT has permission to write to the bus in a given transfer
        self.reading            = False   # Bool indicating if the RT is reading from the databus
        self.writing            = False   # Bool indicating if the RT is writing to the databus

        self.public_key         = None      # Initialized to none type because it is initialized when a function is called
        self.private_key        = None      # Initialized to none type because it is initialized when a function is called
        
        self.events             = deque() # A list of events (str arrays) that come from 1553_simulator

        self.frequency          = 1       # Default tie to sleep between events

        self.BC_public_key      = None

        # For Timer functions, create a variable to check if the RT object still exists before looping execution
        self.exists = "Yes!"

        print("RT {} Init Successful".format(self.num.int)) # Debug line



    # Returns the Remote Terminal ID number (0-31)
    def return_rt_num(self):
        return self.num

    ## TODO: Generate key-pair function to call when a broadcast with non-zero
    #        reserved bits is received
    def gen_key(self):
        return

    def encrypt(self, text,s):
        result = ""

        # transverse the plain text
        for i in range(len(text)):
            char = text[i]
        
            # Encrypt uppercase characters in plain text
            if (char.isupper()):
                result += chr((ord(char) + s-65) % 26 + 65)
            
            # Encrypt lowercase characters in plain text
            else:
                result += chr((ord(char) + s - 97) % 26 + 97)
                
        return result
    
    def decrypt(self, text,s):
        result = ""
        shift = 0 - s
        
        # transverse the cypher text
        for i in range(len(text)):
            char = text[i]
        
            # Decrypt uppercase characters to plain text
            if (char.isupper()):
                result += chr((ord(char) + shift-65) % 26 + 65)
        
            # Decrypt lowercase characters to plain text
            else:
                result += chr((ord(char) + shift-97) % 26 + 97)
        
        return result

    # Function to handle receiving data
    def receive(self):
        # This function handles the logic for when the RT gets a command to RX
        # If the subadress mode is zero or thirty-one the remote terminal will look at the next field
        # to see what the mode code is and take action accordingly
        
        tmp_msg = self.databus.read_BitArray()

        # If the message is a command word, do this
        if (tmp_msg.bin[0:3] == "101"):
            print("RT" + str(self.num.int) + " received command word: " + str(tmp_msg))
            #print("The RT is to receive " + str(tmp_msg.bin[14:19]) + " data words!")
            #print(tmp_msg.bin)
            return

        # If the message is a status word, do this
        elif (tmp_msg.bin[0:3] == "111"):
            print("RT" + str(self.num) + " received status word: " + str(tmp_msg))
            return
        
        # If the message is a data word, do this
        elif (tmp_msg.bin[0:3] == "110"):
            if self.encrypted: # CASE - RT->RT Transfer w/ encryption
                tmp_data = str(chr(int(tmp_msg.bin[3:11],2)) + chr(int(tmp_msg.bin[11:19],2)))
                print("RT" + str(self.num.int) + " received data word " + str(tmp_msg) + " recieved. Data was: \"" + ("".join(tmp_data)) + "\"")
                decrypted_data = self.decrypt(tmp_data, self.shift)
                self.dwords_stored.append(decrypted_data)
                print("RT" + str(self.num.int) +" has decrypted the data. It actually reads: " + decrypted_data)
            else:
                tmp_data = str(chr(int(tmp_msg.bin[3:11],2)) + chr(int(tmp_msg.bin[11:19],2)))
                self.dwords_stored.append(tmp_data)
                print("RT" + str(self.num.int) + " received data word " + str(tmp_msg) + " recieved. Data was: \"" + ("".join(tmp_data)) + "\"")
            return

    # Funciton to return the received data words
    def show_received_data(self):
        print("RT#" +  str(self.num.int) + "'s complete received message is : \"" + ("".join(self.dwords_stored)) + "\"")
        print(self.dwords_stored)
        # Empty list
        self.dwords_stored = []
        return

    # Function to handle transmitting data
    def transmit(self, data):
        if self.encrypted: # CASE - RT->RT Transfer w/ encryption
            tmp_data = str(chr(int(data[3:11],2)) + chr(int(data[11:19],2)))
            print("Data in plaintext: " + tmp_data)
            encrypted_txt = self.encrypt(tmp_data, self.shift)
            print("Data transmitted: " + str(encrypted_txt))
            bs  = Bits('0b'+(''.join(format(i, '08b') for i in bytearray(encrypted_txt, encoding='utf-8'))))
            msg_out = data_word.create_data_word(bs)
            self.databus.write_BitArray(BitArray("0b" + msg_out))

        # Transmit the two characters!
        else:
            self.databus.write_BitArray(BitArray("0b" + data))

        #print(str(data.bin))
        print("RT" + str(self.num.int) + " WROTE BITARRAY - " + str(data))
        print(str(self.databus.read_BitArray()))


    # Function to send a status word on the bus
    def send_status_word(self):
        # Create status word from status of the RT
        print("RT is creating a status word!")
        sendable_status_word = status_word.create_status_word(self.num.int, self.msg_err, self.instrumentation, self.service, \
            0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
        # Add  status word to the databus
        print("RT is sending " + str(sendable_status_word) + " data, which is a status word!")
        self.databus.write_BitArray(sendable_status_word)
        return

    # Read message from bus (20 bits)
    def read_message(self):
        tmp = self.databus.read_BitArray()
        return tmp

    # Fucntion to wait on write permissions to continue execution.
    def wait_for_write_perm(self):
        while(not(self.writing)):
            sleep(0.1)
        return

    # Fucntion to wait on read permissions to continue execution.
    def wait_for_read_perm(self):
        while(not(self.reading)):
            sleep(0.1)
        return


    def process_mode_code(self, mode_code):
        if  (mode_code==BitArray(uint=0, length=5)):	# case 0:  Dynamic Bus Control | No Data Word Associated
            # We are not doing Dynamic Bus Control at this time, but it is valid
            return 
        
        elif (mode_code==BitArray(uint=1, length=5)):	# case 1:  Synchronize (without a data word) | No Data Word Associated
            # Given the nature of this simulation, and the limitations of Python, there is no need / reasonable ability to sync
            return 

        elif (mode_code==BitArray(uint=2, length=5)):	# case 2:  Transmit Status Word | No Data Word Associated
            # Create status word from status of the RT
            sendable_status_word = status_word(self.num, self.msg_err, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            # Add  status word to the databus
            self.databus.write_BitArray(sendable_status_word)
            return 

        elif (mode_code==BitArray(uint=3, length=5)):	# case 3:  Initiate Self Test |  No Data Word Associated
            # There will be no Built-In-Test (BIT) for these RTs. This will just send status.
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
            sendable_status_word = status_word(self.num, self.msg_err, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            self.databus.write_BitArray(sendable_status_word)
            return
        
        elif (mode_code==BitArray(uint=7, length=5)):	# case 7:  Override Inhibit T/F bit  | No Data Word Associated
            # Override terminal flag bit FIRST
            self.terminal = 1
            # Send status word
            sendable_status_word = status_word(self.num, self.msg_err, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            self.databus.write_BitArray(sendable_status_word)
            return
        
        elif (mode_code==BitArray(uint=8, length=5)):	# case 8:  Reset Remote Terminal | No Data Word Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.msg_err, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            self.databus.write_BitArray(sendable_status_word)
            # Reset RT values to default
            self.rx_tx              = BitArray(uint=0, length=1)
            self.msg_err      = BitArray(uint=0, length=1)
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
            sendable_status_word = status_word(self.num, self.msg_err, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)

            data_word_list = []           
            
            for _ in range(4):

                data_word = self.read_message()
                data_word_list.append(data_word.data)
                sleep(self.frequency)

            self.BC_public_key = int(str(data_word_list[0], data_word_list[1], data_word_list[2], data_word_list[3]), 16)

            # After all data words are received the RT should respond with a Status Word to acknowledge that the messages were received
            self.issue_status_word(sendable_status_word)
            return

        elif (mode_code==BitArray(uint=10, length=5)):   # case 10: Transmit Remote Terminal Public Key | 4 Data Words Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.msg_err, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            
            sleep(self.frequency)

            self.issue_status_word(sendable_data_word)

            self.private_key = secrets.randbelow(9223372036854775808)
            self.public_key = secrets.randbelow(9223372036854775808)
            
            full_public_key = BitArray(uint= self.public_key, length=64)
            data_word_list = [full_public_key[:16], full_public_key[16:32], full_public_key[32:48], full_public_key[48:]]

            for data_word in data_word_list:
                    
                public_key_dw       =      self.create_data_word(data_word)
                self.write_message(public_key_dw)
                sleep(self.frequency)
            return
          
        elif (mode_code==BitArray(uint=16, length=5)):	# case 16: Transmit Vector Word | Data Word Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.msg_err, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            self.databus.write_BitArray(sendable_status_word)
            # Send data word containing bits 4-19 of the last command word this RT received, excluding mode code bits
            return
        
        elif (mode_code==BitArray(uint=17, length=5)):	# case 17: Synchronize (with data word) | Data Word Associated
            # Given the nature of this simulation, and the limitations of Python, there is no need / reasonable ability to sync
            return
        
        elif (mode_code==BitArray(uint=18, length=5)):	# case 18: Transmit Last Command Word | Data Word Associated
            sendable_data_word = data_word(self.last_command_word)
            self.databus.write_BitArray(sendable_data_word)
            return
        
        elif (mode_code==BitArray(uint=19, length=5)):  # case 19: Transmit Bit Word |  Data Word Associated
            
            sendable_status_word = status_word(self.num, self.msg_err, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            
            self.databus.write_BitArray(sendable_status_word)
            
            #sendable_data_word = data_word()
            #sendable_data_word.create_data_word()
            return
        
        elif (mode_code==BitArray(uint=20, length=5)):	# case 20: Selected Transmitter Shutdown |  Data Word Associated
            # We are not using redundant bus systems.
            return
        
        elif (mode_code==BitArray(uint=21, length=5)):	# case 21: Override Selected Transmitter Shutdown | Data Word Associated
            # We are not using redundant bus systems.
            return
        
        else:				                            # default: mode_code not defined, set message error bit
            print("There was a mode code word recieved, but the meaning is undefined!")
            self.msg_err = 1
            return

    # Craft status word
    def create_status_word(self):
        msg_out = status_word.create_status_word(self.num, self.msg_err, 0, 0, 0, self.broadcast_command, 0, 0, self.dynamic_bus, 0)
        return msg_out

    def queue_message(self, command):
        '''Takes a command in from 1553_simulator.py and turns it into an event and queues it'''
        self.events.append(command)
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
    
    # Validates that a received status word has no errors
    def validate_status_word(self, status_word):
        self.msg_err = 0
        if (status_word.msg_type_bits !=  "111"):
            self.msg_err = 1
        # Check for odd parity in the 16 data bits (exclude the type bits)
        elif ((status_word.raw_data.count(1) % 2) == 0):
            self.msg_err = 1
        return self.msg_err

    # Sends status word to the bus
    def issue_status_word(self, sendable_status_word):
        self.databus.write_BitArray(sendable_status_word)
        return

    # Validates that a received data word has no errors
    def validate_data_word(self, data_word):
        self.msg_err = 0
        if (data_word.msg_type_bits !=  "101"):
            self.msg_err = 1
        # Check for odd parity
        elif ( (data_word.raw_data.count(1) % 2) == 0):
            self.msg_err = 1
        return self.msg_err

    # Validates that a received command word has no errors
    def validate_command_word(self, command_word):
        self.msg_err = 0
        if (command_word.msg_type_bits != "111"):
            self.msg_err = 1
        # Check for incorrect parity
        elif ((command_word.raw_data.count(1) % 2) == 0):
            self.msg_err = 1
        return self.msg_err

    # RT Destructor
    def __del__(self):
        self.exists = "No."
        del(self)