#!/usr/bin/env python3

# This file implements the functionality of an attacker on the 1553 bus
# For now, it is a placeholder

from threading import Thread, Timer
from datetime import datetime
from os import getcwd
from json import dump
from random import randint
from time import sleep
from bitstring import BitArray
from bus import bus

class attacker(object):

    def __init__(self, atk_type, frequency, terminal_src = 32, terminal_dst = 32 , demo_mode = 0):
        '''Initializes an attack of the type "atk_type" from args.
        Different attack types implement different behavior from this class.'''
        if(type(atk_type) is not str):
            print("First argument should be an attack type. Please use: \n\"DoS\"\n\"Eavesdropping\"\n\"Imitation\"")
            self.__del__()
        self.atk = atk_type
        self.bus = bus()
        self.src = None
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
            if(demo_mode == 0 and (terminal_src == 32 or terminal_dst == 32)):
                print("Can't imitate without a designated terminal number! Two ints 0-30 as arguments, src and dst.")
                self.__del__()
            else:
                if(terminal_src < 0 or terminal_src > 30 or (type(terminal_src) is not int)):
                    print("That was not a valid terminal number. Please pass an integer from 0-30.")
                    self.__del__()
                if(terminal_dst < 0 or terminal_dst > 30 or (type(terminal_dst) is not int)):
                    print("That was not a valid terminal number. Please pass an integer from 0-30.")
                    self.__del__()
                self.src = terminal_src
                Thread(target=self.imitate_start, args=(terminal_src, terminal_dst, frequency, demo_mode)).run()
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

    def stop_eavesdropping(self):
        # Indicate the end of logging if doing an eavesdropping attack
        if(self.atk == "Eavesdropping"):
            event = {"Event" : "Stopped listening in on the bus!"}
            self.addtime(event)
            with open(getcwd() + '/io/jsons/stolen.json', 'a') as event_dumped :
                dump(event, event_dumped)
        self.__del__()

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

    def imitate_start(self, num_src, num_dst, frequency, demo_flag):
        '''Pretends to be a valid RT'''
        self.src = num_src
        if(demo_flag == 1):
            print("Attacker is now going to imitate RT" + str(num_src) + " and send data to RT" + str(num_dst))
        # Shut up the RT that is being imitated. Send command word to listen for the maximum possible time, rendering the RT inert for a while.
        hush_command =  '0b101' + BitArray(uint=num_src, length=5).bin + '0' + '10101' + '11111'
        if(hush_command.count('1') % 2 == 0):
            hush_command = hush_command + '1'
        else:
            hush_command = hush_command + '0'
        self.bus.write_BitArray(BitArray(hush_command))
        #sleep(frequency) # Wait for receptive RT to be silenced
        Timer(frequency, self.imitate_write, [num_src, num_dst, frequency, demo_flag]).start()
    
    def imitate_write(self, num_src, num_dst, frequency, demo_flag):
        sleep(frequency)
        data = ["IM", "RT", str(num_src)]
        if (len(str(data[2])) != 2):
            data[2] = "0" + str(data[2])
        go_ahead = 0
        if(demo_flag == 1):
            go_ahead = 1 # Demo will not wait for a BC to permit speaking
            allowed_sends = 3
        # Now, wait for BC instruction to transmit.    
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
                go_ahead = 1
                allowed_sends = int(msg[14:19].bin, 2)
                break
        while(allowed_sends > len(data)):
            data.append("!!")
        for char_pair in data:
            char1 = bin(ord(char_pair[0]))[2:]
            while len(char1) < 8:
                char1 = "0" + char1
            char2 = bin(ord(char_pair[1]))[2:]
            while len(char2) < 8:
                char2 = "0" + char2
            data_word = "0b110" + char1 + char2
            if(data_word.count('1') % 2 == 0):
                data_word = data_word + "1"
            else:
                data_word = data_word + "0"
            if(demo_flag == 1):
                print("Attacker is sending \"" + char_pair + "\" to RT" + str(num_dst))
            self.bus.write_BitArray(BitArray(data_word))
            sleep(frequency) # Give time for message to be read
        return

    # Destructor
    def __del__(self):
        '''This is the destructor of the attacker object'''
        self.exists = "No."
        # Re-activate the imitated RT after ceasing imitation the attack
        if(self.atk == "Imitation"):
            src_bits = bin(self.src)[2:]
            while len(src_bits) < 5:
                src_bits = "0" + src_bits
            tmp = '0b101' + src_bits + '1' + '00000' + '00010'
            if(tmp.count('1') % 2 == 0):
                tmp = tmp + "1"
            else:
                tmp = tmp + "0"
            self.bus.write_BitArray(BitArray(tmp))
        del(self)

# Examples of use:
# attacker("DoS", 1) - Randomly sets/clears a bunch of bits on the bus about ten times a second, preventing effective 
#   communication
# attacker("Eavesdropping", 1) - Checks the bus every second and logs its contents. Extracts and logs information from 
#   data words.
# attacker("Imitation", 1, terminal_src = 2, terminal_dst = 3) - Sends a pre-coded message to RT03 as though it was 
#   from RT02 every second.