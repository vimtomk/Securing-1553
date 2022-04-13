#!/usr/bin/env python3

from bitstring import Bits, BitArray

class message(object):

    def __init__(self, msg):
    
        if len(msg) != 20:
            print("ERROR: Message given not equal to 20 bits!")
        
        # The first three bits
        #self.msg_type_bits   = BitArray(uint=msg[0:3], length=3)   #[2:5]
        # The remaining seventeen bits
        #self.raw_data        = BitArray(uint=msg[3:19], length=16) #[5:-1]
        # The last bit
        #self.parity_bit      = BitArray(uint=msg[19], length=1)    #[-1:]
        
        # Construct the whole message
        self.msg             = BitArray(msg)
        
        # Setting the string msg_type based on bits 
        '''
        if   (self.msg_type_bits.bin == "101"):
            self.msg_type = "Command Word"
        elif (self.msg_type_bits.bin == "110"):
            self.msg_type = "Data Word"
        elif (self.msg_type_bits.bin == "111"):
            self.msg_type = "Status Word"
        else:
            self.msg_type = "Error - Sync is off and is set to: "+self.msg_type_bits.bin
        '''
        
    # Prints message type bits in literal binary
    def return_message_type_bin(self):
        ob = self.msg_type_bits
        return ob

    # Print data type as string of binary with leading 0b
    def print_message_type_data_str(self):
        print(self.msg_type_bits.bin)

    # Print message type as human-readable string
    def print_message_type_str(self):
        print(self.msg_type)

    # Print entire raw, literal binary message
    def print_raw_data_bits(self):
        print(self.raw_data.bin)

    # Return parity bit
    def return_parity_bit(self):
        ob = self.parity_bit.bin
        return ob

    # Print parity bit
    def print_parity_bit(self):
        print(self.parity_bit.bin)

    # Check if there is error in message
    def check_err(self):
        '''Checks a message for a parity error, assuming ODD parity.
        Returns true if there is an error, false otherwise.'''
        # Calculate parity and compare it to the current parity bit
        if (BitArray(uint=(self.msg.count(1)) % 2 == 0, length=1) and self.msg.parity_bit.bin):
            return False
        else:
            return True

    # Destructor
    def __del__(self):
        del(self)

class command_word(object):
    
    # This has no type-casting, for some reason, so be sure to only put in 16 bits
    def create_command_word_with_data(self, data=BitArray(uint=0, length=16)):
        self.msg_type   = BitArray(uint=5,      length=3)
        self.rt_addr    = data.bin[0:5]    # Five bit flag
        self.tx_rx      = data.bin[5]      # One bit flag
        self.sa_mode    = data.bin[6:11]   # Five bit field
        self.mode_code  = data.bin[12:]    # Five bit field

        self.msg = BitArray(data)
        
    # Calculate parity of data and append it to the message.
        self.msg.append(BitArray(uint=((self.msg.count(1)) % 2 == 0), length=1))
        
    # Once parity is calculated, prepend the msg type.
        self.msg.prepend(self.msg_type)
        return self.msg


    # Initialize each message field, turn the data to binary, and pack the bits.
    def create_command_word(rt_addr, tx_rx, sa_mode, mode_code):
        msg_type  = BitArray(uint=5,         length=3)     # 3 bit field
        rt_addr   = BitArray(uint=rt_addr,   length=5)     # 5 bit field
        tx_rx     = BitArray(uint=tx_rx,     length=1)     # 1 bit flag
        sa_mode   = BitArray(uint=sa_mode,   length=5)     # 5 bit field
        mode_code = BitArray(uint=mode_code, length=5)     # 5 bit field

    # Create the "data" part of the message.
        msg = BitArray(rt_addr)
        msg.append(tx_rx)
        msg.append(sa_mode)
        msg.append(mode_code)
    # Calculate parity of data and append it to the message.
        msg.append(BitArray(uint=((msg.count(1)) % 2 == 0), length=1))
        
    # Once parity is calculated, prepend the msg type.
        msg.prepend(msg_type)
        return msg

class data_word(object):

    # Initialize each message field, turn the data to binary, and pack the bits.
    def create_data_word(dat):
        msg_type = BitArray(uint=6,        length=3)   # 3 bit field
        #self.data     = BitArray(uint=dat,     length=16)  # 16 bit field
        
    # Create the "data" part of the message.
        msg = BitArray(dat)

    # Calculate parity of data and append it to the message.
        msg.append(BitArray(uint=((msg.count(1)) % 2 == 0), length=1))
        
    # Once parity is calculated, prepend the msg type.
        msg.prepend(msg_type)
        return msg.bin
        
class status_word(object):

    def create_status_word_with_data(data):    # data is a 
        msg_type   = BitArray(uint=7, length=3) # 3 bit field
        rt_addr    = data.bin[0:5]              # Five bit field
        msg_err    = data.bin[5]                # One bit flag
        instrum    = data.bin[6]                # One bit flag
        serv_req   = data.bin[7]                # One bit flag
        reserved   = data.bin[8:11]             # Three bit flag
        broad_comm = data.bin[11]               # One bit flag
        busy       = data.bin[12]               # One bit flag
        sub_flag   = data.bin[13]               # One bit flag
        dyn_bc     = data.bin[14]               # One bit flag
        term_flag  = data.bin[15]               # One bit flag

        # Create the "data" part of the message.
        msg = BitArray(data)

        # Calculate parity of data and append it to the message.
        msg.append(BitArray(uint=((msg.count(1)) % 2 == 0), length=1))

        # Once parity is calculated, prepend the msg type.
        msg.prepend(msg_type)

        # Print full message in binary without <0b> at the beginning.
        return msg.bin


    def create_status_word(rt_addr, msg_err, instrum, serv_req, reserved, broad_comm, busy, sub_flag, dyn_bc, term_flag):

        # Initialize each message field, turn the data to binary, and pack the bits.
        msg_type   = BitArray(uint=7,          length=3)  # 3 bit field
        rt_addr    = BitArray(uint=rt_addr,    length=5)  # 5 bit field
        msg_err    = BitArray(uint=msg_err,    length=1)  # 1 bit flag
        instrum    = BitArray(uint=instrum,    length=1)  # 1 bit flag
        serv_req   = BitArray(uint=serv_req,   length=1)  # 1 bit flag
        reserved   = BitArray(uint=reserved,   length=3)  # 3 bit field
        broad_comm = BitArray(uint=broad_comm, length=1)  # 1 bit flag
        busy       = BitArray(uint=busy,       length=1)  # 1 bit flag
        sub_flag   = BitArray(uint=sub_flag,   length=1)  # 1 bit flag
        dyn_bc     = BitArray(uint=dyn_bc,     length=1)  # 1 bit flag
        term_flag  = BitArray(uint=term_flag,  length=1)  # 1 bit flag
        
        # Create the "data" part of the message.
        msg = BitArray(rt_addr)
        msg.append(msg_err)
        msg.append(instrum)
        msg.append(serv_req)
        msg.append(reserved)
        msg.append(broad_comm)
        msg.append(busy)
        msg.append(sub_flag)
        msg.append(dyn_bc)
        msg.append(term_flag)

        # Calculate parity of data and append it to the message.
        msg.append(BitArray(uint=((msg.count(1)) % 2 == 0), length=1))
        
        # Once parity is calculated, prepend the msg type.
        msg.prepend(msg_type)

        # Print full message in binary without <0b> at the beginning.
        #print(self.msg.bin)

        return msg.bin


"""Sample code to turn string into binary (helpful when taking in string)
from bitstring import Bits, BitArray
str = "Hello"
bs  = Bits('0b'+(''.join(format(i, '08b') for i in bytearray(str, encoding='utf-8'))))
bs.bin
"""