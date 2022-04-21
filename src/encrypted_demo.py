#!/usr/bin/env python3
# This file demos an encrypted data word transfer

from time import sleep
from bus import bus
from bc import bc
from rt import rt

print("Starting the MIL-STD-1553 Encrypted Version Demonstration.")

print("\nPress enter to start the demonstration...")
input()
print("Starting encrypted communications between 2 RTs...")
sleep(1)

# Declare type of encryption and key
shift = 15
print("Doing simple ceasar cypher, shift of " + str(shift))
sleep(.5)

# Start bus
print("Initializing data bus...")
databus = bus()
sleep(.5)

# Start RTs
print("Initializing Remote Terminals...")
rt1 = rt(1, crypt=True, key=shift)
rt2 = rt(2, crypt=True, key=shift)
sleep(.5)

# Start BC
print("Initializing Bus Controller...")
bc0 = bc(0, rt_array=[rt1, rt2])
sleep(.5)

# Perform RT->RT transfer event
print("Creating event RT01->RT02 Transfer!")
bc0.events.append(["RT03","RT04","1","1","5","data","PLAINTXT"])
bc0.RT_RT_Transfer(rt1, rt2, bc0.events[0][6])
rt1.show_received_data()

# Shut down RTs
print("Shutting down the Remote Terminals...")
rt1.__del__()
rt2.__del__()
sleep(.5)

# Shut down BC
print("Shutting down the Bus Controller...")
bc0.__del__()
sleep(.5)

# Delete bus
print("Shutting down data bus...")
databus.__del__()
sleep(.5)