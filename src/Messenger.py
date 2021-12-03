#!/usr/bin/python3

# This file reads in data from a .csv file and uses it to send data across the bus in an automated fashion
import socket
import os
import sys
import time
from threading import Thread
from Bus_Controller.BC_Simulator import Bus_Controller

global bc_listener_thread
global rt_listener_thread


def executeonce(threadid, msg, delay):
    "Executes a message once, after a given delay"
    time.sleep(delay)
    #print("Thread #" + str(threadid) + " is sending Message: " + msg) ###DEBUG#LINE###
    # Send data
    rt_addr = threadid - 1
    if (rt_addr >= 32):
    	# 1553 only supports up to 32 RTs
    	sys.exit(0)
    if (rt_addr < 10):
    	arg1 = "0" + str(rt_addr)
    else:
        arg1 = str(rt_addr)
    Bus_Controller().send_data_to_rt(arg1, "01", msg)
    Bus_Controller().receive_data_from_rt(arg1, "01", "07")

def loopexecute(threadid, msg, delay, frequency):
    "Executes a message indefinitely, at a given frequency"
    time.sleep(delay)
    rt_addr = threadid - 1
    if (rt_addr >= 32):
    	# 1553 only supports up to 32 RTs
    	sys.exit(0)
    if (rt_addr < 10):
    	arg1 = "0" + str(rt_addr)
    sec_delay = float(1) // frequency
    while True:
        time.sleep(sec_delay)
        Bus_Controller().send_data_to_rt(arg1, "01", msg)
        Bus_Controller().receive_data_from_rt(arg1, "01", "07")

# Default case executes without argument, otherwise read in from file
if (len(sys.argv) >= 3):
    print("Only one or zero arguments is accepted.")
    print("If no arguments, default file is read.")
    print("If an argument is given, it should be the name of the input csv in this folder.")
    sys.exit(0)
if (len(sys.argv) == 1):
    infile = open(os.getcwd() + '/io/csvs/default.csv', 'r')
else:
    infile = open(sys.argv[1], 'r')

# Read in all lines from the file
msglines = infile.readlines()
infile.close()

# Parse lines and create threads to do tasks
threads = []
tid = 0
for msg in msglines:
    # [0] is message, [1] is delay (s), [2] is loop flag, [3] is loop frequency (Hz)
    # all else is stored in [4] and disregarded...
    tid += 1
    parsed = msg.split(',', 4)
    #print("Message: " + parsed[0]) ###DEBUG#LINE###
    #print("Delay is of " + parsed[1] + " seconds.") ###DEBUG#LINE###
    #print("Loop flag is set to: " + parsed[2]) ###DEBUG#LINE###
    if (int(parsed[2]) == 0):
        # Pass to function that executes once
        #print("Message executes once.") ###DEBUG#LINE###
        t = Thread(target=executeonce, args=(tid, parsed[0], float(parsed[1])))
    else:
    	# Pass to function that executes in a loop
    	#print("Message executes in a loop of frequency " + parsed[3] + " Hz.") ###DEBUG#LINE###
    	t = Thread(target=loopexecute, args=(tid, parsed[0], float(parsed[1]), float(parsed[3])))
    threads.append(t)
    t.start()

#if __name__ == "__main__":
    # Add code to print out messages sent when just this file is run

# CSV File reader capabilities - 
#
# Input must be read in from .csv files
# Therefore, must be able to parse data line by line with commas as seperators
#
# The specific input file must be given via ???
# There must be fields to take -
# - message to be sent?
# - how long until message is sent?
# - to loop / not to loop?
# - if looping, what frequency/how often?
# For example, "This is a message.,1,0,0" is just sending the string "This is a message." after 1s with no loop.
# Alternatively, "This is spam!,0,1,.5" is looping the message "This is spam!" at .5Hz, or once every 2 seconds.