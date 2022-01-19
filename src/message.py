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
    
    def __init__(self, rt_addr, tx_rx, sa_mode, mode_code):
        self.rt_addr   = bin(rt_addr)       # 5 bit field
        self.tx_rx     = bin(tx_rx)         # 1 bit flag
        self.sa_mode   = bin(sa_mode)       # 5 bit field
        self.mode_code = bin(mode_code)     # 5 bit field

class data_word:
    
    def __init__(self, data):
        self.data = data                    # 16 bit field

class status_word:
    
    def __init__(self, rt_addr, msg_err, instrum, serv_req, reserved, broad_comm, busy, sub_flag, dyn_bc, term_flag):
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
        
        

        # This is henious but Python has forced my hand

        self.msg_type.append(self.rt_addr)
        self.msg_type.append(self.msg_err)
        self.msg_type.append(self.instrum)
        self.msg_type.append(self.serv_req)
        self.msg_type.append(self.reserved)
        self.msg_type.append(self.broad_comm)
        self.msg_type.append(self.busy)
        self.msg_type.append(self.sub_flag)
        self.msg_type.append(self.dyn_bc)
        self.msg_type.append(self.term_flag)

        # Setting odd parity bit.
        self.msg_type.append(BitArray(uint=((self.msg_type.count(0)) & 1), length=1))

        print(self.msg_type.bin) # Full message here in binary without annoying <0b'>