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
        
        self.rcvd_broadcast     = 0       # Flag to indicate if RT received broadcast message for Transmit Last Status Word
        self.msg_err            = 0       # Flag to indicate if last received message from BC had an error
                                          # Condition 1 : RT receives a word with an error (parity)
                                          # Condition 2 : RT expects a stream of data words, but there is a gap (a cycle is missed getting the next data word)
                                          # Condition 3 : RT receives a command it does not have the functionality to execute (unimplemented mode code)
                                          # Condition 4 : RT somehow receives the wrong number of data words (missing data words, extra data words)
        
        self.last_status_word   = BitArray(uint=0, length=20)   # Use to store last status word so we can transmit
        self.last_command_word  = BitArray(uint=0, length=20)   # Use to store last received command word
        self.dwords_expected    = 0       # A counter that keeps track of how many data words the terminal is still expecting to receive
        self.dwords_stored      = ""      # Stores a string of data words as they come in, eventually being output to the terminal.
        self.write_permission   = 0       # Count indicating how many data words this RT has permission to write to the bus

        self.public_key         = None      # Initialized to none type because it is initialized when a function is called
        self.private_key        = None      # Initialized to none type because it is initialized when a function is called
        
        self.events             = deque() # A list of events (str arrays) that come from 1553_simulator

        # For Timer functions, create a variable to check if the RT object still exists before looping execution
        self.exists = "Yes!"

        print("RT {} Init Successful".format(self.num.int)) # Debug line

        # Start listening immediately
        self.main()



    # Returns the Remote Terminal ID number (0-31)
    def return_rt_num(self):
        return self.num
    
    # Sets Write Permission
    def set_write_perm(self, bool):
        self.write_permission = bool
        return

    ## TODO: Generate key-pair function to call when a broadcast with non-zero
    #        reserved bits is received
    def gen_key(self):

        return

    # Event Handler
    def event_handler(self):
        if len(self.events > 0):
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
            
            # RT -> BC
            if (event[0][:2] == "RT" and event[1][:2] == "BC"):
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
            
        else:
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
        if(tmp[0] == 1 and tmp[1] == 1 and tmp[2] == 0): #and (self.dwords_expected > 0)): # If a data word 110, and we are expecting a data word
            print("--RT " + str(self.num.int) + " says: Data Word received by RT.\nData is: " + chr(int(tmp.bin[3:11],2)) + chr(int(tmp.bin[11:19],2)))
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
                print("--RT " + str(self.num.int) + " says: This message was a broadcast!")
                pass
            if(tmp[0] == 1 and tmp[1] == 0 and tmp[2] == 1): # If a command word 101
                # Check to see if the command word contains a Mode Code or a Word Count
                if((tmp[9:14] == "00000") or tmp[9:14] == "11111"): # If subaddress field is either of these, it is a mode code in the next 5-bit field
                    print("Command Word received!\nMode code is: " + tmp.bin[14:19])
                    # Send the mode code to the processor function
                    self.process_mode_code(BitArray('0b' + tmp.bin[14:19]))
                else: # This command word is permitting the terminal to send data words
                    print("Command Word received!\nWord Count is: " + int("0b" + tmp.bin[14:19], 2))
                    self.write_permission = int("0b" + tmp.bin[14:19], 2)
            if(tmp.count(1) % 2 == 0): # Failed parity check
                self.error = 1
            #else: # Passed parity check
            elif(tmp[0] == 1 and tmp[1] == 1 and tmp[2] == 1): # If a status word 111
                print("--RT " + str(self.num.int) + " says: Status Word received!\nStatus was-\nError Flag: " + tmp.bin[8] + "\nService Request: " + tmp.bin[10] + "\nBusy bit: " + tmp.bin[15])
                if(tmp.count(1) % 2 == 0): # Failed parity check
                    self.error = 1
            #else: # Passed parity check
        #else: # This terminal was definitely not the intended recipient of the message

    def write_message_timer(self):
        '''At the end of a time interval, this function is called and if the terminal has a need and the permissions
        to write to the bus, it will do so.'''
        if((self.write_permission == 0) or (len(self.events) == 0)): # If there is no permission to write anything or nothing to write, return immediately.
            return
        print("Writing a message to the bus!")
        #self.databus.write_BitArray(self.event_to_word(self.events.pop()))
        return

    # RT -> BC
    ## Remote Terminal to Bus Controller Transfer
    ## The Bus Controller sends one transmit command word to a Remote Terminal
    ## The Remote Terminal then sends a single Status word
    ## immediately followed by 1 to 32 words.
    def RT_BC_Transfer(self, rt_num_tx, data):

        # Creates an array of two chars that will later be turning into 16 bit data words
        array = self.string_to_tokens(data)
        msg_count = len(array)

        # Listen for command word
        sleep(0.5)
        bc_command_word = self.read_message()

        # Transmit status word
        rt_status_word = self.create_status_word()
        self.issue_status_word(rt_status_word)
        sleep(1)

        # Now send the data words
        bit_string_list = []
        for strn in array:
            bs  = Bits('0b'+(''.join(format(i, '08b') for i in bytearray(strn, encoding='utf-8'))))
            bit_string_list.append(bs)

        for bs in bit_string_list:
            sleep(1)
            data_msg = self.create_data_word(bs)
            self.issue_data_word(data_msg)

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
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
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

            # After all data words are received the RT should respond with a Status Word to acknowledge that the messages were received
            self.issue_status_word(sendable_status_word)

            return

        elif (mode_code==BitArray(uint=10, length=5)):   # case 10: Transmit Remote Terminal Public Key | 4 Data Words Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
                0, self.broadcast_command, self.busy, self.subsystem, self.dynamic_bus, self.terminal)
            
            sleep(1)

            self.issue_status_word(sendable_data_word)

            self.private_key = secrets.randbelow(9223372036854775808)
            self.public_key = secrets.randbelow(9223372036854775808)
            
            full_public_key = BitArray(uint= self.public_key, length=64)
            data_word_list = [full_public_key[:16], full_public_key[16:32], full_public_key[32:48], full_public_key[48:]]

            for data_word in data_word_list:
                    
                public_key_dw       =      self.create_data_word(data_word)
                self.write_message(public_key_dw)
                sleep(1)

            
            
            return
          
        elif (mode_code==BitArray(uint=16, length=5)):	# case 16: Transmit Vector Word | Data Word Associated
            # Send status word FIRST
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
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
            
            sendable_status_word = status_word(self.num, self.message_error, self.instrumentation, self.service, \
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
            self.message_error = 1
            return

    # Craft status word
    def create_status_word(self):
        msg_out = status_word.create_status_word(self.num, self.msg_err, 0, 0, 0, self.broadcast_command, 0, 0, self.dynamic_bus, 0)
        return msg_out

    # Main loop for listening to bus.
    def main(self):
        # This while-True loop may hold up execution of the whole program if main() is run!
        # If this does hold up execution, switch to threading version (or just use read_message_timer?)
        if(self.exists == "Yes!"): # If the BC has been removed, stop execution
            threading.Timer(.25, self.main()).start() # Currently configured : Check each quarter second.
        #while True:
            
            ## TODO: Once logic is understood for each transfer type, 
            # implement the if-else, and set up contextual decision making
            # i.e., understand what to do with the next message

            # Grabs first message from bus if bus not empty and not in use
            if not(self.databus.is_empty()):
                # Wait for databus to not be in use.
                while (self.databus.is_in_use()):
                    sleep(0.005)
                    pass
                tmp_msg = self.read_message()
                
                # Use RT method that passes bus queue to RT and processes the first message on the queue
                if (tmp_msg.bin[3:8] == BitArray(uint=self.num, length=5)) and (tmp_msg.bin[0:3] == "101"): # Command Word
                    
                    # Store copy of relevent bits
                    self.last_command_word = tmp_msg
                    self.received_msgs.append(tmp_msg)

                    # This will set the Remote Terminal's Transfer/Receiving Mode
                    if tmp_msg[8] == BitArray(uint=1, length=1):
                            # This puts the Remote Terminal in Transfer mode
                            self.rx_tx_mode == BitArray(uint=1, length=1)    
                    else:
                            # Keeps RT in Receiving mode
                            self.rx_tx_mode == BitArray(uint=0, length=1)        
                    
                    # If the subadress mode is zero or thirty-one the remote terminal will look at the next field
                    # to see what the mode code is and take action accordingly
                    if (tmp_msg.bin[9:14] == BitArray(uint=0, length=5) or tmp_msg.bin[9:14] == BitArray(uint=31, length=5)):
                    
                        self.process_mode_code(tmp_msg.bin[9:14])
                    
                    # The mode code field will else represent the number of words the RT needs to transmit or receive
                    else:   
                        
                        # Creates a message count of how many words to either transmit or receive
                        msg_count = tmp_msg.bin[14:19]
                         
                        # The RT will create data words to transmit 
                        if self.rx_tx_mode == 1:
                            
                            # Looks at the event list to see what message to send 
                            sending_msg = self.events.pop()
                            char_pairs = self.string_to_tokens(sending_msg[6])
                            
                            # Create data words
                            data_send_list = []
                            for char_pair in char_pairs:
                                complete_data_word = "0b110" + bin(ord(char_pair[0]))[2:] + bin(ord(char_pair[1]))[2:]
                                if(complete_data_word.count(1) % 2 == 0):
                                    complete_data_word = complete_data_word + "1"
                                else:
                                    complete_data_word = complete_data_word + "0"
                                complete_data_word = BitArray(complete_data_word)
                                data_send_list.append(complete_data_word)

                            # Send data words in time to be taken in by recipient
                            #TODO: Finish
                            # This maybe could be handled by queueing up messages for write_message_timer to send out
                            pass
                        
                        # The RT will prepare to receive data words 
                        else:
                            
                            data_word_list = []

                            for msg in range(0, msg_count):
                                
                                # Reads the data word off of the data bus
                                msg = self.read_message()
                                char1 = chr(int(msg[0:8], 2))
                                char2 = chr(int(msg[8:], 2))
                                data_word_list.append(char1 + char2)
                                sleep(1)
                                
                            for ch in data_word_list:
                                message += ch

                            print("RT#" +  self.num + " has received data word with '" + message + "'")
                        
                            # Send status word back to BC
                            status_word = self.create_status_word()
                            self.issue_status_word(status_word)
                            
                # The RT has received a broadcast message                
                elif (tmp_msg.rt_addr.bin == BitArray(uint=31, length=5).bin):
                    #TODO: Watch for broadcasted status words w/ non-zero 
                    #      reserved bits as a form of synchronizing keys 
                    return

                # We have encountered some type of error in the message type bits
                # (not defined as data/command/status word)
                else: 
                    print("RT#" + self.num + " has received a word with unknown message type.")

            # Databus is either empty, or we are done getting messages so sleep.
            #sleep(0.25) # Currently configured : Check each quarter second.
        else:
            return
        return
    # End of main()
    
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