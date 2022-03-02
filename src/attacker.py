#!/usr/bin/env python3

# This file implements the functionality of an attacker on the 1553 bus
# For now, it is a placeholder

from threading import Timer
from datetime import datetime
from os import getcwd
from json import dump
from bus import bus

class attacker(object):
    # Initializer
    def __init__(self, atk_type):
        '''Initializes an attack of the type "atk_type" from args.
        Different attack types implement different behavior from this class.'''
        self.atk = atk_type
        self.bus = bus()
        if(atk_type == "DoS"):
            pass
        elif(atk_type == "Eavesdropping"):
            event = {"Event" : "Started listening in on the bus!"}
            self.addtime(event)
            with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped :
                dump(event, event_dumped)
            pass
        elif(atk_type == "Imitation"):
            self.num = None #TODO: Figure out how to take in the terminal number to imitate
            pass
        pass #TODO: Add code to begin execution of different attacks based on input attack type

    def deny_service(self, duration):
        '''Fills the bus with noise to deny effective communication'''
        pass #TODO: Add code to repeatedly write to the bus randomly, interfering with any messages being sent or read.

    def eavesdrop(self, frequency):
        '''Keeps its own log of all bus events, spying on messages not intended to be overheard'''
        Timer(self.frequency, self.eavesdrop, [frequency]).start() # Call repeatedly on a timer
        event = {}
        self.addtime(event)
        event["Overheard Message"] = bus.read_BitArray()
        with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped :
            dump(event, event_dumped)

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

    def imitate(self, rt, frequency, duration):
        '''Pretends to be a valid RT'''
        pass #TODO: Add code to send forged messages under the guise of another device

    # Destructor
    def __del__(self):
        '''This is the destructor of the attacker object'''
        if(self.atk == "Eavesdropping"):
            event = {"Event" : "Stopped listening in on the bus!"}
            self.addtime(event)
            with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped :
                dump(event, event_dumped)
        del(self)