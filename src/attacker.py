#!/usr/bin/env python3

# This file implements the functionality of an attacker on the 1553 bus
# For now, it is a placeholder

from threading import Timer
from datetime import datetime
from os import getcwd
from json import dump
from random import randint
from bus import bus

class attacker(object):

    def __init__(self, atk_type, frequency):
        '''Initializes an attack of the type "atk_type" from args.
        Different attack types implement different behavior from this class.'''
        if(type(atk_type) is not str):
            print("First argument should be an attack type. Please use: \nDoS\nEavesdropping\nImitation")
            self.__del__()
        self.atk = atk_type
        self.bus = bus()
        if(atk_type == "DoS"):
            self.deny_service(frequency / 10)
        elif(atk_type == "Eavesdropping"):
            event = {"Event" : "Started listening in on the bus!"}
            self.addtime(event)
            with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped:
                dump(event, event_dumped)
            self.eavesdrop(frequency)
        elif(atk_type == "Imitation"):
            print("Can't imitate without a designated terminal number! Two ints 0-30 as arguments, src and dst.")
            self.__del__()
        else:
            print("Sorry, that attack type is not recognized or implemented. Exiting...")
            self.__del__()
        pass #TODO: Add code to begin execution of different attacks based on input attack type

    #TODO: Since Python doesn't allow multiple _init_s for different argument counts, find a workaround...
    #def __init__(self, atk_type, frequency, terminal_num_src, terminal_num_dst):
        '''Initializes an attack of the type "atk_type", specifically "Imitation".
        An alternate init is required to get the terminal number to imitate.'''
        '''if(type(atk_type) is not str):
            print("First argument should be an attack type. Please use: \nDoS\nEavesdropping\nImitation")
            self.__del__()
        if(atk_type == "DoS"):
            print("Too many arguments for this attack type! Did you mean to Imitate?")
            self.__del__()
        elif(atk_type == "Eavesdropping"):
            print("Too many arguments for this attack type! Did you mean to Imitate?")
            self.__del__()
        elif(atk_type == "Imitation"):
            if(terminal_num_src < 0 or terminal_num_src > 30 or (type(terminal_num_src) is not int)):
                print("That was not a valid terminal number. Please pass an integer from 0-30.")
                self.__del__()
            if(terminal_num_dst < 0 or terminal_num_dst > 30 or (type(terminal_num_dst) is not int)):
                print("That was not a valid terminal number. Please pass an integer from 0-30.")
                self.__del__()
            self.imitate(terminal_num_src, terminal_num_dst, frequency)
            pass #TODO: Define behavior for imitation
        else:
            print("Sorry, that attack type is not recognized or implemented. Exiting...")
            self.__del__()'''

    def deny_service(self, frequency):
        '''Fills the bus with random noise to deny effective communication'''
        Timer(frequency, self.deny_service, [frequency]).start() # Call repeatedly on a timer
        self.bus.write_bit(randint(0, 1), randint(0, 19))
        self.bus.write_bit(randint(0, 1), randint(0, 19))
        self.bus.write_bit(randint(0, 1), randint(0, 19))
        return

    def eavesdrop(self, frequency):
        '''Keeps its own log of all bus events, spying on messages not intended to be overheard'''
        Timer(frequency, self.eavesdrop, [frequency]).start() # Call repeatedly on a timer
        event = {}
        self.addtime(event)
        tmp_message = bus.read_BitArray()
        event["Overheard Message"] = tmp_message
        with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped:
            dump(event, event_dumped)
        # Special additional action for data words - Capture and convert the actual data to chars
        if(tmp_message[0] == 1 and tmp_message[1] == 1 and tmp_message[2] == 0): # If a data word 110...
            event = {"Event" : "Data word intercepted!"}
            event["Data Characters"] = chr(int(tmp_message.bin[3:11],2)) + chr(int(tmp_message.bin[11:19],2))
            with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped:
                dump(event, event_dumped)
        return

    def addtime(self, dictionary):
        '''Takes a dictionary and adds entries for the approximate date and time of function call, down to the microsecond'''
        temp_dt = datetime.now()
        dictionary['time_year'] = temp_dt.strftime('%Y')
        dictionary['time_month'] = temp_dt.strftime('%m')
        dictionary['time_day'] = temp_dt.strftime('%d')
        dictionary['time_hour'] = temp_dt.strftime('%H')
        dictionary['time_minute'] = temp_dt.strftime('%M')
        dictionary['time_second'] = temp_dt.strftime('%S')
        dictionary['time_microsecond'] = temp_dt.strftime('%f')
        return

    def imitate(self, num_src, num_dst, frequency):
        '''Pretends to be a valid RT'''
        data = ["IM", "RT", str(num_src)]
        if len(data[2] != 2):
            data[2] = "0" + data[2]
        #TODO: Add code to send forged messages under the guise of another device
        #-Read in messages like a normal RT
        #-When the BC sends a command word that lets this RT speak, send pre-coded message instead
        pass

    # Destructor
    def __del__(self):
        '''This is the destructor of the attacker object'''
        # Indicate the end of logging if doing an eavesdropping attack
        if(self.atk == "Eavesdropping"):
            event = {"Event" : "Stopped listening in on the bus!"}
            self.addtime(event)
            with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped :
                dump(event, event_dumped)
        del(self)

# Examples of use:
# attacker("DoS", 1) - Randomly sets/clears a bunch of bits on the bus about ten times a second, preventing effective communication
# attacker("Eavesdropping", 1) - Checks the bus every second and logs its contents. Extracts and logs information from data words.
# attacker("Imitation", 1, 2, 3) - Sends a pre-coded message to RT03 as though it was from RT02 every second.