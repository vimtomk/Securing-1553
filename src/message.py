#!/usr/bin/env python3
from bitstring import Bits, BitArray, BitString

class message(object):

    def __init__(self, msg):
    
        if len(bin(int(msg, base=2))) > 22:
            print("ERROR: Message given longer than 20 bits!")
            self.__del__()
            exit()
        # The first three bits
        self.msg_type_bits   = bin(msg)[2:5]
        # The remaining seventeen bits
        self.raw_data        = bin(msg)[5:-1]
        self.parity_bit      = bin(msg)[-1:]
        
        print(self.msg_type_bits)
        # Setting the string msg_type based on bits
        if   (self.msg_type_bits == "101"):
            self.msg_type = "Command Word"
        elif (self.msg_type_bits == "110"):
            self.msg_type = "Data Word"
        elif (self.msg_type_bits == "111"):
            self.msg_type = "Status Word"
        else:
            self.msg_type = "Error - Sync = 100"
        
    # Prints message type bits in literal binary
    def return_message_type_bin(self):
        ob = bin(int(self.msg_type_bits, base=2))
        return ob

    # Print data type as string of binary with leading 0b
    def print_message_type_data_str(self):
        print(str(self.msg_type_bits)[2:-1], end='')

    # Print message type as human-readable string
    def print_message_type_str(self):
        print(self.msg_type)

    # Print entire raw, literal binary message
    def print_raw_data_bits(self):
        print(self.raw_data)

    # Return parity bit
    def return_parity_bit(self):
        ob = ob = bin(int(self.parity_bit, base=2))
        return ob

    # Print parity bit
    def print_parity_bit(self):
        print(self.parity_bit)

    # Def self
    def __del__(self):
        del(self)

class command_word:
    
    # Initialize each message field, turn the data to binary, and pack the bits.
    def __init__(self, rt_addr, tx_rx, sa_mode, mode_code):
        self.msg_type  = BitArray(uint=5,         length=3)     # 3 bit field
        self.rt_addr   = BitArray(uint=rt_addr,   length=5)     # 5 bit field
        self.tx_rx     = BitArray(uint=tx_rx,     length=1)     # 1 bit flag
        self.sa_mode   = BitArray(uint=sa_mode,   length=5)     # 5 bit field
        self.mode_code = BitArray(uint=mode_code, length=5)     # 5 bit field

    # Create the "data" part of the message.
        self.msg = BitArray(self.rt_addr)
        self.msg.append(self.tx_rx)
        self.msg.append(self.sa_mode)
        self.msg.append(self.mode_code)

    # Calculate parity of data and append it to the message.
        self.msg.append(BitArray(uint=((self.msg.count(1)) % 2 == 0), length=1))
        
    # Once parity is calculated, prepend the msg type.
        self.msg.prepend(self.msg_type)

class data_word:
    
    # Initialize each message field, turn the data to binary, and pack the bits.
    def __init__(self, data):
        self.msg_type = BitArray(uint=6,        length=3)   # 3 bit field
        self.data     = BitArray(uint=data,     length=16)  # 16 bit field
        
    # Create the "data" part of the message.
        self.msg = BitArray(self.data)

    # Calculate parity of data and append it to the message.
        self.msg.append(BitArray(uint=((self.msg.count(1)) % 2 == 0), length=1))
        
    # Once parity is calculated, prepend the msg type.
        self.msg.prepend(self.msg_type)
        

class status_word:
    
    def __init__(self, rt_addr, msg_err, instrum, serv_req, reserved, broad_comm, busy, sub_flag, dyn_bc, term_flag):

        # Initialize each message field, turn the data to binary, and pack the bits.
        self.msg_type   = BitArray(uint=7,          length=3)  # 3 bit field
        self.rt_addr    = BitArray(uint=rt_addr,    length=5)  # 5 bit field
        self.msg_err    = BitArray(uint=msg_err,    length=1)  # 1 bit flag
        self.instrum    = BitArray(uint=instrum,    length=1)  # 1 bit flag
        self.serv_req   = BitArray(uint=serv_req,   length=1)  # 1 bit flag
        self.reserved   = BitArray(uint=reserved,   length=3)  # 3 bit field
        self.broad_comm = BitArray(uint=broad_comm, length=1)  # 1 bit flag
        self.busy       = BitArray(uint=busy,       length=1)  # 1 bit flag
        self.sub_flag   = BitArray(uint=sub_flag,   length=1)  # 1 bit flag
        self.dyn_bc     = BitArray(uint=dyn_bc,     length=1)  # 1 bit flag
        self.term_flag  = BitArray(uint=term_flag,  length=1)  # 1 bit flag
        
        # Create the "data" part of the message.
        self.msg = BitArray(self.rt_addr)
        self.msg.append(self.msg_err)
        self.msg.append(self.instrum)
        self.msg.append(self.serv_req)
        self.msg.append(self.reserved)
        self.msg.append(self.broad_comm)
        self.msg.append(self.busy)
        self.msg.append(self.sub_flag)
        self.msg.append(self.dyn_bc)
        self.msg.append(self.term_flag)

        # Calculate parity of data and append it to the message.
        self.msg.append(BitArray(uint=((self.msg.count(1)) % 2 == 0), length=1))
        
        # Once parity is calculated, prepend the msg type.
        self.msg.prepend(self.msg_type)

        # Print full message in binary without <0b> at the beginning.
        print(self.msg.bin)


"""Sample code to turn string into binary (helpful when taking in string)
from bitstring import Bits, BitArray
str = "Hello"
bs  = Bits('0b'+(''.join(format(i, '08b') for i in bytearray(str, encoding='utf-8'))))
bs.bin
"""
