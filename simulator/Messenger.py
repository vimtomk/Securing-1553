# This file reads in data from a .csv file and uses it to send data across the bus in an automated fashion
import socket
import os
import sys
from threading import Thread

# TODO : Add code to function "loopexecute"
# TODO : Add code to function "executeonce"
# TODO : Add code to print the sent message to terminal at the time of sending, if this file is run alone

def loopexecute(id, msg, frequency):
    "Executes a message indefinitely, at a given frequency"

def executeonce(id, msg, delay):
    "Executes a message once, after a given delay"

# Default case executes without argument, otherwise read in from file
if (len(sys.argv) >= 3):
    print("Only one or zero arguments is accepted.")
    print("If no arguments, default file is read.")
    print("If an argument is given, it should be the name of the input csv in this folder.")
    sys.exit(0)
if (len(sys.argv) == 1):
    infile = open(os.getcwd() + '/io/csvs/defualt.csv', 'r')
else:
    infile = open(sys.argv[1], 'r')

# Read in all lines from the file
msglines = infile.readlines()
infile.close()

# Parse lines and create threads to do tasks
threads = []
for msg in msglines:
    # [0] is message, [1] is loop flag, [2] is loop frequency (Hz) OR delay (s)
    # all else is stored in [3] and disregarded
    parsed = msg.split(',', 3)
    if (parsed[1] == 0):
        # Pass to function that executes once
        t = Thread(target=executeonce, args=(parsed[0], parsed[2]))
    else:
    	# Pass to function that executes in a loop
    	t = Thread(target=executeonce, args=(parsed[0], parsed[2]))
    threads.append(t)
    t.start()

if __name__ == "__main__":
    # Add code to print out messages sent when just this file is run

# CSV File reader capabilities - 
#
# Input must be read in from .csv files
# Therefore, must be able to parse data line by line with commas as seperators
#
# The specific input file must be given via ???
# There must be fields to take -
# - message to be sent
# - to loop / not to loop
# - if looping, what frequency/how often?
# For example, "This is a message.,0,1" is just sending the string "This is a message." after 1s with no loop.
# Alternatively, "This is spam!,1,.5" is looping the message "This is spam!" at .5Hz, or once every 2 seconds