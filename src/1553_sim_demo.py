#!/usr/bin/env python3
# This file demos BC->RT, RT->BC, RT->RT; in that order

from time import sleep
from bus import bus
from bc import bc
from rt import rt
from bitstring import BitArray
import threading

print("Starting the MIL-STD-1553 Databus, Python Simulation Demonstration.")
print("Order of simulation demonstration is...\nBC -> RT Transfer\nRT -> BC Transfer\nRT -> RT Transfer")

################################################################################################################################

# Demonstrate BC -> RT transfer
print("\nPress enter to continue to the BC -> RT Transfer demonstration...")
input()
print("Starting BC -> RT Transfer...")
sleep(2)

# Start bus for this demo
print("Initializing data bus...")
databus = bus()
sleep(.5)

# Start BC, RT
print("Initializing Bus Controller...")
bc_p1 = bc(0)
sleep(.5)

print("Initializing Remote Terminal...")
rt_p1 = rt(1)
sleep(.5)

##TODO: Implement a demonstration of the BC to RT transfer
# Start BC, RT
print("Initializing Bus Controller...")
bc_p1 = bc(0, rt_array=[rt_p1])

threading.Timer(1, bc_p1.main()).start()
threading.Timer(1, rt_p1.main()).start()

bc_p1.BC_RT_Transfer(rt_p1.num.int, "Hi")


# Shut down RTs, BC
print("Shutting down the Remote Terminal...")
rt_p1.__del__()
sleep(.5)
print("Shutting down the Bus Controller...")
bc_p1.__del__()
sleep(.5)
# Delete bus for next demo
print("Shutting down data bus...")
databus.__del__()
sleep(.5)

################################################################################################################################

# Demonstrate RT -> BC transfer
print("\nPress enter to continue to the RT -> BC Transfer demonstration...")
input()
print("Starting RT -> BC Transfer...")
sleep(2)

# Start bus for this demo
print("Initializing data bus...")
databus = bus()
sleep(.5)
# Start BC, RT
print("Initializing Bus Controller...")
bc_p2 = bc(0)
sleep(.5)
print("Initializing Remote Terminal...")
rt_p2 = rt(2)
sleep(.5)

##TODO: Implement a demonstration of the RT to BC transfer

# Shut down RTs, BC
print("Shutting down the Remote Terminal...")
rt_p2.__del__()
sleep(.5)
print("Shutting down the Bus Controller...")
bc_p2.__del__()
sleep(.5)
# Delete bus for next demo
print("Shutting down data bus...")
databus.__del__()
sleep(.5)

################################################################################################################################

# Demonstrate RT -> RT transfer
print("\nPress enter to continue to the RT -> RT Transfer demonstration...")
input()
print("Starting RT -> RT Transfer...")
sleep(2)

# Start bus for this demo
print("Initializing data bus...")
databus = bus()
sleep(.5)
# Start BC, RT
print("Initializing Bus Controller...")
bc_p3 = bc(0)
sleep(.5)
print("Initializing Remote Terminal...")
rt_p3_1 = rt(3)
rt_p3_2 = rt(4)
sleep(.5)

##TODO: Implement a demonstration of the RT to RT transfer

# Shut down RTs, BC
print("Shutting down the Remote Terminals...")
rt_p3_1.__del__()
rt_p3_2.__del__()
sleep(.5)
print("Shutting down the Bus Controller...")
bc_p3.__del__()
sleep(.5)
# Delete bus for next demo
print("Shutting down data bus...")
databus.__del__()
sleep(.5)



## TODO: FINISH BC->RT TRANSFER