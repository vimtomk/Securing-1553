#!/usr/bin/env python3

# This file will set up a few situations on a 1553 data bus and execute cyberattacks against the users of the bus
# Data will be collected, proving the effectiveness of the cyberattacks and vulnerabilities of 1553
# This file may later be modified to implement the "fixed" version of the 1553, and demonstrate the effectiveness of our fixes

from time import sleep
from bus import bus
from bc import bc
from attacker import attacker
from bitstring import BitArray
from rt import rt

#TODO: add code to take a copy of all messages and output them to the 

def string_to_tokens(in_string):
        '''Takes in a string and returns a list of 2-character pairs from that string.
        If the string's length is not divisible by 2, the final character is accompanied by a space.'''
        out_tokens = []
        i = int(len(in_string)/2)
        if(len(in_string) % 2):
            # String length is odd. A space needs to be padded at the end.
            i = i + 1
        for j in range(0,i):
            if(len(in_string[2 * j:]) == 1):
                out_tokens.append( in_string[2 * j] + " " )
            else:
                out_tokens.append( in_string[2 * j] + in_string[2 * j + 1])
        return out_tokens

print("Starting the attacks demonstration.")
print("Order of attacks will be DoS, then eavesdropping, then imitation.")

#-PART 1 : DoS Attack------------------
# In this part, we will prove that the 1553 is vulnerable to DoS attacks as a result of every terminal being assumed to act in good faith
# A compromised terminal, or new terminal plugged into the bus (as in this demo), is able to speak without permissions from the BC
# Our attacker will take a normal bus conversation and interfere with junk data, scrambling data and confusing terminals
print("\nPress enter to continue to the DoS attack...")
input()
print("Now starting the DoS attack demonstration...")
sleep(2)

# Start bus
print("Initializing data bus...")
databus = bus()
sleep(.5)
print("Initializing RTs...")
rt1_dos = rt(1)
rt2_dos = rt(2)
msg_tokens = string_to_tokens("Hello, RT02!")
sleep(.5)
print("No DoS: RT01 is sending a message to RT02")
complete_msg = ""
for token in msg_tokens:
    print("RT01 is sending \"" + token + "\" to RT02!")
    char1 = bin(ord(token[0]))[2:]
    while len(char1) < 8:
        char1 = "0" + char1
    char2 = bin(ord(token[1]))[2:]
    while len(char2) < 8:
        char2 = "0" + char2
    dword = "0b110" + char1 + char2
    if(dword.count("1") % 2 == 0):
        dword = dword + "1"
    else:
        dword = dword + "0"
    rt1_dos.databus.write_BitArray(BitArray(dword))
    sleep(1.5)
    read_word = rt2_dos.databus.read_BitArray()
    print("RT02 got a message!")
    sleep(.1)
    if(read_word.bin[:3] == "110"):
        print("Data word recieved. Data was: \"" + chr(int(read_word.bin[3:11],2)) + chr(int(read_word.bin[11:19],2)) + "\"")
        complete_msg = complete_msg + (chr(int(read_word.bin[3:11],2)) + chr(int(read_word.bin[11:19],2)))
    else:
        print("Message could not be recognized as a data word...")
    if(read_word.count("1") % 2 == 0):
        print("Message parity check failed!")
    else:
        print("Message parity check passed.")
    sleep(1.5)
sleep(2)
print("\nRT02's final recieved message is: \"" + complete_msg + "\"\n")
sleep(2)
print("Now starting the actual attack portion...")
sleep(1)
print("With DoS: RT01 is sending a message to RT02")

# Start the attacking terminal
print("Initializing the attacking terminal...")
spammer = attacker("DoS", 3)
sleep(2)
complete_msg = ""
for token in msg_tokens:
    print("RT01 is sending \"" + token + "\" to RT02!")
    char1 = bin(ord(token[0]))[2:]
    while len(char1) < 8:
        char1 = "0" + char1
    char2 = bin(ord(token[1]))[2:]
    while len(char2) < 8:
        char2 = "0" + char2
    dword = "0b110" + char1 + char2
    if(dword.count("1") % 2 == 0):
        dword = dword + "1"
    else:
        dword = dword + "0"
    rt1_dos.databus.write_BitArray(BitArray(dword))
    sleep(1.5)
    read_word = rt2_dos.databus.read_BitArray()
    print("RT02 got a message!")
    sleep(.1)
    if(read_word.bin[:3] == "110"):
        print("Data word recieved. Data was: \"" + chr(int(read_word.bin[3:11],2)) + chr(int(read_word.bin[11:19],2)) + "\"")
        complete_msg = complete_msg + (chr(int(read_word.bin[3:11],2)) + chr(int(read_word.bin[11:19],2)))
    else:
        print("Message could not be recognized as a data word...")
    if(read_word.count("1") % 2 == 0):
        print("Message parity check failed!")
    else:
        print("Message parity check passed.")
    sleep(1.5)
sleep(2)
print("\nRT02's final recieved message is: \"" + complete_msg + "\"\n")
sleep(2)

# Start cleaning up
# Shut down attacker
print("Shutting down the attacking terminal...")
spammer.__del__()
sleep(3)
# Shut down RTs
print("Shutting down RTs...")
rt1_dos.__del__()
rt2_dos.__del__()
sleep(.3)
# Delete bus for next demo
print("Shutting down data bus...")
databus.__del__()

#-PART 2 : Eavesdropping Attack--------
# In this part, we will prove that the 1553 emulator is vulnerable to Eavesdropping attacks as a result of there being no encryption
# We will have terminals engage in normal data transfer. A compromised terminal, or new terminal on the bus (as in this demo), is able to hear everything
# Our attacker will log all communications from the bus, and if it overhears a data word it will log what was heard as text

print("\nPress enter to continue to the eavesdropping attack...")
input()
print("Now starting the eavesdropping attack demonstration...")
sleep(2)

# Start bus
print("Initializing data bus...")
databus = bus()
sleep(.5)
print("Initializing RTs...")
rt1_evs = rt(1)
rt2_evs = rt(2)
msg_tokens = string_to_tokens("Hello, RT02!")
sleep(.5)
print("Initializing the attacking terminal...")
snooper = attacker("Eavesdropping", 3)
sleep(.5)

# Start data transfer
complete_msg = ""
for token in msg_tokens:
    print("RT01 is sending \"" + token + "\" to RT02!")
    char1 = bin(ord(token[0]))[2:]
    while len(char1) < 8:
        char1 = "0" + char1
    char2 = bin(ord(token[1]))[2:]
    while len(char2) < 8:
        char2 = "0" + char2
    dword = "0b110" + char1 + char2
    if(dword.count("1") % 2 == 0):
        dword = dword + "1"
    else:
        dword = dword + "0"
    rt1_evs.databus.write_BitArray(BitArray(dword))
    sleep(1.5)
    read_word = rt2_evs.databus.read_BitArray()
    print("RT02 got a message!")
    sleep(.1)
    if(read_word.bin[:3] == "110"):
        print("Data word recieved. Data was: \"" + chr(int(read_word.bin[3:11],2)) + chr(int(read_word.bin[11:19],2)) + "\"")
        complete_msg = complete_msg + (chr(int(read_word.bin[3:11],2)) + chr(int(read_word.bin[11:19],2)))
    else:
        print("Message could not be recognized as a data word...")
    if(read_word.count("1") % 2 == 0):
        print("Message parity check failed!")
    else:
        print("Message parity check passed.")
    sleep(1.5)
print("RT02's final recieved message is: \"" + complete_msg + "\"")

# Start cleaning up
# Shut down attacker
print("Shutting down the snooping terminal...")
snooper.stop_eavesdropping()
sleep(3)
# Shut down RTs
print("Shutting down RTs...")
rt1_evs.__del__()
rt2_evs.__del__()
sleep(.3)
# Delete bus for next demo
print("Shutting down data bus...")
databus.__del__()
sleep(.3)
print("Check the log file in \\io\\jsons called \"stolen.json\" \n")

#-PART 3 : Imitation Attack------------
# In this part, we will prove the 1553 is vulnerable to imitation attacks
# We will have the attacker attach to the bus, and send a command word to the imitated RT to listen for a lot of data words
# Due to 1553's specifics, this causes the target RT to never try and send messages until it gets a "Transmit Last Status" word from the BC
# But since the BC didn't tell the RT to listen, the BC doesn't think to check the status of the RT. So the RT is effectively disabled
# until the attacker releases control by sending a "Transmit Last Status" word and re-activating the RT it was imitating

print("Press enter to continue to the imitation attack...")
input()
print("Now starting the imitation attack demonstration...")
sleep(2)
# Start bus
print("Initializing data bus...")
databus = bus()
sleep(.5)
print("Initializing RTs...")
rt1_imt = rt(1)
rt2_imt = rt(2)
sleep(.5)
char_pair = "Hi"
print("The real RT01 is sending \"" + char_pair + "\" to RT02")
char1 = bin(ord(char_pair[0]))[2:]
while len(char1) < 8:
    char1 = "0" + char1
char2 = bin(ord(char_pair[1]))[2:]
while len(char2) < 8:
    char2 = "0" + char2
dword = "0b110" + char1 + char2
if(dword.count("1") % 2 == 0):
    dword = dword + "1"
else:
    dword = dword + "0"
rt1_imt.databus.write_BitArray(BitArray(dword))
sleep(1.5)
read_word = rt2_imt.databus.read_BitArray()
print("RT02 got a message!")
complete_msg = ""
sleep(.1)
if(read_word.bin[:3] == "110"):
    print("Data word recieved. Data was: \"" + chr(int(read_word.bin[3:11],2)) + chr(int(read_word.bin[11:19],2)) + "\"")
    complete_msg = complete_msg + (chr(int(read_word.bin[3:11],2)) + chr(int(read_word.bin[11:19],2)))
else:
    print("Message could not be recognized as a data word...")
if(read_word.count("1") % 2 == 0):
        print("Message parity check failed!")
else:
    print("Message parity check passed.")
sleep(1.5)
print("Now starting the imitation attack. Initializing the attacker...")
imposter = attacker("Imitation", 1.5, terminal_src = 1, terminal_dst = 2, demo_mode = 1)
sleep(1.5)
com_word = rt1_imt.databus.read_BitArray()
if((com_word.bin[:3] == "101") and (com_word.bin[3:8] == "00001")):
    print("RT01 got a command word!")
    if((com_word.bin[8] == '0') and not ((com_word.bin[9:14] == '00000') or (com_word.bin[9:14] == '11111'))):
        print("RT01's command was to listen in for " + str(int(com_word[14:19].bin, 2)) \
            + " data words!\nThis effectively silences the terminal until it is asked to send status...")
    else:
        print("RT01's command was not to listen...")
else:
    print("RT01 failed to get the silencing command...")
sleep(1.5)
complete_msg = ""
i = 0
while(i < 3):
    read_word = rt2_imt.databus.read_BitArray()
    rt2_imt.databus.clear_bus() # Make sure the same message isn't being read repeatedly
    print("RT02 got a message!")
    sleep(.1)
    if(read_word.bin[:3] == "110"):
        print("Data word recieved. Data was: \"" + chr(int(read_word.bin[3:11],2)) + chr(int(read_word.bin[11:19],2)) + "\"")
        complete_msg = complete_msg + (chr(int(read_word.bin[3:11],2)) + chr(int(read_word.bin[11:19],2)))
    else:
        print("Message could not be recognized as a data word...")
        print("The message was : " + read_word.bin)
    if(read_word.count("1") % 2 == 0):
        print("Message parity check failed!")
    else:
        print("Message parity check passed.")
    i = i + 1
    sleep(1.5)
print("RT02's final recieved message is: \"" + complete_msg + "\"")

# Start cleaning up
print("Shutting down the imitation terminal and returning control to the original...")
imposter.__del__()
sleep(2)

# Shut down RTs
print("Shutting down RTs...")
rt1_imt.__del__()
rt2_imt.__del__()
sleep(.3)
# Delete bus for next demo
print("Shutting down data bus...")
databus.__del__()