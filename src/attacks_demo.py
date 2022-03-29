#!/usr/bin/env python3

# This file will set up a few situations on a 1553 data bus and execute cyberattacks against the users of the bus
# Data will be collected, proving the effectiveness of the cyberattacks and vulnerabilities of 1553
# This file may later be modified to implement the "fixed" version of the 1553, and demonstrate the effectiveness of our fixes

from time import sleep
from bus import bus
from bc import bc
from rt import rt

print("Starting the attack demonstration.")
sleep(.3)
print("Order of attacks will be DoS, then eavesdropping, then imitation.")
sleep(.3)

#-PART 1 : DoS Attack------------------
# In this part, we will prove that the 1553 is vulnerable to DoS attacks as a result of every terminal being assumed to act in good faith
# A compromised terminal, or new terminal plugged into the bus (as in this demo), is able to speak without permissions from the BC
# Our attacker will take a normal bus conversation and interfere with junk data, scrambling data and confusing terminals

print("Now starting the DoS attack demonstration...")
sleep(.3)
# Start bus
print("Initializing data bus...")
databus = bus()
sleep(.3)
print("Initializing RTs...")
rt1_dos = rt(1)
rt2_dos = rt(2)
sleep(.3)
print("Initializing BC...")
bc_dos = bc(0, [1, 2])
sleep(.3)

##TODO: Implement the DoS Attack demo
# Start the attacking terminal
print("Starting the attacking terminal...")
pass
sleep(3)

# Start cleaning up
# Shut down attacker
print("Shutting down the attacking terminal...")
pass
sleep(3)
# Shut down BCs and RTs
print("Shutting down BC...")
bc_dos.__del__()
sleep(.3)
print("Shutting down RTs...")
rt1_dos.__del__()
rt2_dos.__del__()
sleep(.3)
# Delete bus for next demo
print("Shutting down data bus...")
databus.__del__()
sleep(1)

#-PART 2 : Eavesdropping Attack--------
# In this part, we will prove that the 1553 emulator is vulnerable to Eavesdropping attacks as a result of there being no encryption
# We will have terminals engage in normal data transfer. A compromised terminal, or new terminal on the bus (as in this demo), is able to hear everything
# Our attacker will log all communications from the bus, and if it overhears a data word it will log what was heard as text

print("Now starting the eavesdropping attack demonstration...")
##TODO: Implement the Eavesdropping  demo


#-PART 3 : Imitation Attack------------
##TODO: Once the bus is ready to go and the Imitation attacker has been tested, populate this part with comments and code...

print("Now starting the imitation attack demonstration...")