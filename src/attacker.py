#!/usr/bin/env python3

# This file implements the functionality of an attacker on the 1553 bus
# For now, it is a placeholder

from threading import Timer
from datetime import datetime
from os import getcwd
from json import dump
from random import randint
from time import sleep
from bitstring import BitArray
from bus import bus

class attacker(object):

    def __init__(self, atk_type, frequency, terminal_src = 32, terminal_dst = 32):
        '''Initializes an attack of the type "atk_type" from args.
        Different attack types implement different behavior from this class.'''
        if(type(atk_type) is not str):
            print("First argument should be an attack type. Please use: \n\"DoS\"\n\"Eavesdropping\"\n\"Imitation\"")
            self.__del__()
        self.atk = atk_type
        self.bus = bus()
        self.exists = "Yes!"
        if(atk_type == "DoS"):
            self.deny_service(frequency / 10)
        elif(atk_type == "Eavesdropping"): # Do not make more than one eavesdropper in a simulation!
            event = {"Event" : "Started listening in on the bus!"}
            self.addtime(event)
            with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped:
                dump(event, event_dumped)
            self.eavesdrop(frequency)
        elif(atk_type == "Imitation"):
            if(terminal_src == 32 or terminal_dst == 32):
                print("Can't imitate without a designated terminal number! Two ints 0-30 as arguments, src and dst.")
                self.__del__()
            else:
                if(terminal_src < 0 or terminal_src > 30 or (type(terminal_src) is not int)):
                    print("That was not a valid terminal number. Please pass an integer from 0-30.")
                    self.__del__()
                if(terminal_dst < 0 or terminal_dst > 30 or (type(terminal_dst) is not int)):
                    print("That was not a valid terminal number. Please pass an integer from 0-30.")
                    self.__del__()
                self.imitate(terminal_src, terminal_dst, frequency)
            pass #TODO: Define behavior for imitation
        else:
            print("Sorry, that attack type is not recognized or implemented. Exiting...")
            self.__del__()

    def deny_service(self, frequency):
        '''Fills the bus with random noise to deny effective communication'''
        if(self.exists == "Yes!"): # Check if the object still exists
            Timer(frequency, self.deny_service, [frequency]).start() # Call repeatedly on a timer
        else:
            return
        self.bus.write_bit(randint(0, 1), randint(0, 19))
        self.bus.write_bit(randint(0, 1), randint(0, 19))
        self.bus.write_bit(randint(0, 1), randint(0, 19))
        return

    def eavesdrop(self, frequency):
        '''Keeps its own log of all bus events, spying on messages not intended to be overheard'''
        if(self.exists == "Yes!"): # Check if the object still exists
            Timer(frequency, self.eavesdrop, [frequency]).start() # Call repeatedly on a timer
        else:
            return
        event = {}
        self.addtime(event)
        tmp_message = self.bus.read_BitArray()
        event["Overheard Message"] = tmp_message.bin
        with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped:
            dump(event, event_dumped)
            event_dumped.write("\n")
        # Special additional action for data words - Capture and convert the actual data to chars
        if(tmp_message[0] == 1 and tmp_message[1] == 1 and tmp_message[2] == 0): # If a data word 110...
            event = {"Event" : "Data word intercepted!"}
            event["Data Characters"] = chr(int(tmp_message.bin[3:11],2)) + chr(int(tmp_message.bin[11:19],2))
            with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped:
                dump(event, event_dumped)
                event_dumped.write("\n")
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
        ##TODO: When the bus is ready to go, and we have a decent simulation, try this attack in that simulation...
        data = ["IM", "RT", str(num_src)]
        if len(data[2] != 2):
            data[2] = "0" + data[2]
        # Shut up the RT that is being imitated. Send command word to listen for the maximum possible time, rendering the RT inert for a while.
        hush_command =  '0b101' + BitArray(uint=num_src, length=5).bin + '0' + '10101' + '11111'
        if(hush_command.count(1) % 2 == 0):
            hush_command.append('1')
        else:
            hush_command.append('0')
        self.bus.write_BitArray(BitArray(hush_command))
        # Now, wait for BC instruction to transmit.
        go_ahead = 0
        while go_ahead == 0:
            sleep(frequency)
            msg = self.bus.read_BitArray()
            if(msg[:3].bin != "101"): # Not a command word
                continue
            if(msg[3:8] != BitArray(uint=num_src, length=5).bin): # Not word targeting this imitated RT
                continue
            if(msg[8] == False): # Not a word that commands to transmit
                continue
            if((msg[9:14] == '00000') or (msg[9:14] == '11111')): # Command word w/ mode code, ignore.
                continue
            else: # This RT is being given time to speak on the bus. Initiate transfer, and send data. Pad with "!!"
                allowed_sends = int(msg[14:19].bin, 2)
                while(allowed_sends > len(data)):
                    data.append("!!")
                for char_pair in data:
                    data_word = '0b110' + BitArray(unit=ord(char_pair[0]), length=8).bin + BitArray(unit=ord(char_pair[1]), length=8).bin
                    if(data_word.count(1) % 2 == 0):
                        data_word.append("1")
                    else:
                        data_word.append("0")
                    self.bus.write_BitArray(BitArray(data_word))
                    sleep(frequency) # Give time for message to be read
        return

    # Destructor
    def __del__(self):
        '''This is the destructor of the attacker object'''
        # Indicate the end of logging if doing an eavesdropping attack
        if(self.atk == "Eavesdropping"):
            event = {"Event" : "Stopped listening in on the bus!"}
            self.addtime(event)
            with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped :
                dump(event, event_dumped)
        self.exists = "No."
        del(self)

# Examples of use:
# attacker("DoS", 1) - Randomly sets/clears a bunch of bits on the bus about ten times a second, preventing effective 
#   communication
# attacker("Eavesdropping", 1) - Checks the bus every second and logs its contents. Extracts and logs information from 
#   data words.
# attacker("Imitation", 1, terminal_src = 2, terminal_dst = 3) - Sends a pre-coded message to RT03 as though it was 
#   from RT02 every second.