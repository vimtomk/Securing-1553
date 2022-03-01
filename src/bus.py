#!/usr/bin/env python3

# This file defines the "bus" class and its functionality

from bitstring import BitArray 

class bus(object):
    # Bus is a singleton, all terminals should access this and ONLY this bus. Enforce through modified "__new__"
    def __new__(cls):
        '''Overrides the normal __new__ to ensure this object is the one and only instance'''
        if not hasattr(cls, 'instance'):
            cls.instance = super(bus, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        '''Initializes the bus, and all values are cleared by default'''
        self.__dA9tA9mA6nG0lE9dd = BitArray('0x00000') # 20 bits of '0'
        #print("Bus Init Successful") # Debug line
        # Bus values SHOULD ONLY BE ACCESSED THROUGH FUNCTIONS.
        # Python doesn't allow private variables, so the name is mangled to discourage direct access.

    # Most "accurate" way to read from bus, as information is read bit-by-bit.
    def read_bit(self, pos):
        '''Returns a 1 or 0, from a position 0-19 on the bus. 
        Call multiple times to be more accurate to the real way bus data is recieved.'''
        if( ( pos < 0 ) or (19 < pos ) ):
            return # Some mistake was made in calling this function, do nothing.
        return int(self.__dA9tA9mA6nG0lE9dd[pos])

    # Most "accurate" way to write to bus, as information is written bit-by-bit.
    def write_bit(self, val, pos):
        '''Takes a 1 or 0, and overwrites a position 0-19 on the bus. 
        Call multiple times to be more accurate to the real way bus data is sent.'''
        if( ( pos < 0 ) or (19 < pos ) or ( val < 0 ) or ( 1 < val) ):
            return # Some mistake was made in calling this function, do nothing.
        self.__dA9tA9mA6nG0lE9dd[pos] = val
        return

    # Fast, easy way to read from bus.
    def read_BitArray(self):
        '''Gets the data in the bus, and returns it ALL AT ONCE as a BitArray'''
        return self.__dA9tA9mA6nG0lE9dd

    # Fast, easy way to write to bus.
    def write_BitArray(self, in_data):
        '''Takes in a BitArray, and overwrites bus data ALL AT ONCE'''
        if(len(in_data) != 20):
            return # Not an array of length 20, do not write!
        for value in in_data:
            if not ( (in_data[value] == True) or (in_data[value] == False) ):
                return # Not a BitArray, do not write!
        self.__dA9tA9mA6nG0lE9dd = in_data
        return

    # Quick, callable bus wipe
    def clear_bus(self):
        '''Sets all 20 bits on the bus to 0'''
        self.__dA9tA9mA6nG0lE9dd = BitArray('0x00000') # 20 bits of '0'
        return

    # Quick way to tell if bus is empty for if statements
    def is_empty(self):
        '''Returns a TRUE if the bus is all 0s, returns FALSE otherwise'''
        if (self.read_bit(0) == 0):
            return True
        else:
            return False

    # Destructor. Just deletes the object - DO NOT USE UNTIL EXITING SIMULATION!
    def __del__(self):
        '''This is the destructor of the bus object. It just does del(self)'''
        del(self)

#bus = bus() # Un-comment to initialize the bus on import, usually not needed

# Example of the class in action that you can try in console:
# Setup
#   from bus import bus
#   from bitstring import BitArray
#   bus = bus()
# Reading pt. 1 - Demonstrating reading the bus all at once
#   print(bus.read_BitArray())
#   print(bus.read_BitArray().bin)
# Writing pt. 1 - Demonstrating writing the bus all at once
#   bus.write_BitArray(BitArray('0x12345'))
#   print(bus.read_BitArray())
#   print(bus.read_BitArray().bin)
# Writing pt. 2 - Demonstrating writing the bus bit by bit
#   bus.write_bit(1, 0)
#   bus.write_bit(1, 1)
#   bus.write_bit(1, 2)
#   bus.write_bit(1, 3)
#   bus.write_bit(0, 4)
#   bus.write_bit(0, 5)
#   bus.write_bit(0, 6)
#   bus.write_bit(0, 7)
#   print(bus.read_BitArray().bin)
# Note: This can write the whole bus bit-by-bit with a for() loop iterating from 0 to 19
# Reading pt. 2 - 
#   bus.read_bit(0)
#   bus.read_bit(1)
#   bus.read_bit(4)
#   bus.read_bit(5)
# Note: This can read the whole bus bit-by-bit with a for() loop iterating from 0 to 19