#!/usr/bin/env python3

from bitstring import Bits, BitArray

class message(object):
    def __init__(self, type = None, data = None):
        pass

    def __del__(self):
        del(self)

class command_word(message):
    pass

class data_word(message):
    pass

class status_word(message):
    pass