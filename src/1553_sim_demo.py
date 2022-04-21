#!/usr/bin/env python3
# This file demos BC->RT, RT->BC, RT->RT; in that order

from time import sleep
from bus import bus
from bc import bc
from rt import rt
from bitstring import BitArray
#import threading
#import multiprocessing
#from multiprocessing import *

print("Starting the MIL-STD-1553 Databus, Python Simulation Demonstration.")
print("Order of simulation demonstration is...\nBC -> RT Transfer\nRT -> BC Transfer\nRT -> RT Transfer")

################################################################################################################################

# Demonstrate BC -> RT transfer
print("\nPress enter to continue to the BC -> RT Transfer demonstration...")
input()
print("Starting BC -> RT Transfer...")
sleep(1)

# Start bus for this demo
print("Initializing data bus...")
databus = bus()
sleep(.5)

# Start BC, RT
#print("Initializing Bus Controller...")
#bc_p1 = bc(0)
#sleep(.5)

print("Initializing Remote Terminal...")
rt_p1 = rt(1)
sleep(.5)

# Start BC, RT
print("Initializing Bus Controller...")
bc_p1 = bc(0, rt_array=[rt_p1])
sleep(.5)

print("Creating event BC->RT01 Transfer!")
bc_p1.events.append(["BC","RT01","1","1","10","data","Hello"])

print(bc_p1.events[0])

print("Bus status, is empty? :" + str(rt_p1.databus.is_empty()))
bc_cmd = bc_p1.create_command_word(rt_p1.num.int, bc_p1.rx.int, bc_p1.zero.int, 3)
print("BC command being written is " + str(bc_cmd))
bc_p1.write_message(bc_cmd)
print("Bus status, is empty? :" + str(rt_p1.databus.is_empty()))
print("RT command word being read is " + str(rt_p1.databus.read_BitArray()))
rt_p1.receive()
print("BC sending data to RT: \"hello\"")
bc_p1.BC_RT_Transfer(rt_p1, bc_p1.events[0][6])

rt_p1.show_received_data()

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
sleep(1)

# Start bus for this demo
print("Initializing data bus...")
databus = bus()
sleep(.2)
# Start BC, RT
print("Initializing Bus Controller...")
bc_p2 = bc(0)
sleep(.2)
print("Initializing Remote Terminal...")
rt_p2 = rt(2)
sleep(.2)

bc_p2 = bc(0, rt_array=[rt_p2])
print("Creating event RT02->BC Transfer!")
bc_p2.events.append(["RT02","BC","1","1","5","data","Howdy"])

bc_p2.RT_BC_Transfer(rt_p2, bc_p2.events[0][6])

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
sleep(0.5)

# Start bus for this demo
print("Initializing data bus...")
databus = bus()
sleep(.1)
# Start BC, RT
print("Initializing Bus Controller...")
#bc_p3 = bc(0)
sleep(.1)
print("Initializing Remote Terminals...")
rt_p3_1 = rt(3)
rt_p3_2 = rt(4)
sleep(.1)

bc_p3 = bc(0, rt_array=[rt_p3_1, rt_p3_2])
print("Creating event RT03->RT04 Transfer!")
bc_p3.events.append(["RT03","RT04","1","1","5","data","Heeeey"])

bc_p3.RT_RT_Transfer(rt_p3_1, rt_p3_2, bc_p3.events[0][6])

# Shut down RTs, BC
print("Shutting down the Remote Terminals...")
rt_p3_1.__del__()
rt_p3_2.__del__()
sleep(.2)
print("Shutting down the Bus Controller...")
bc_p3.__del__()
sleep(.2)
# Delete bus for next demo
print("Shutting down data bus...")
databus.__del__()
sleep(.2)