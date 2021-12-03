#!/usr/bin/python3


class message(object):


    def __init__(self, msg):
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
        

    def return_message_type_bin(self):
        ob = bin(int(self.msg_type_bits, base=2))
        print(ob)
        return type(ob)


    def print_message_type_data_str(self):
        print(str(self.msg_type_bits)[2:-1])

    def print_message_type_str(self):
        print(self.msg_type)


    def print_raw_data_bits(self):
        print(self.raw_data)

    def print_parity_bit(self):
        print(self.parity_bit)


    def __del__(self):
        del(self)


