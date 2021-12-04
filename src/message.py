#!/usr/bin/env python3


class message(object):


    def __init__(self, msg):
        if len(bin(msg)) > 22:
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


