#!/usr/bin/env python3

from bus import bus
import bc, rt, bm, os, sys

databus = bus()     # Points to the shared bus
bc_num  = 0         # Terminal Number of the BC
bm_num  = 0         # Terminal Number of the BM
rt_nums = []        # List of RT numbers
time_interval = 0   # How long, in seconds, each time interval should be
script = []         # Queue of information from input .csv

def parse_csv():
    '''Parses out a .csv file into the initialization parameters and action script.
    The argument for the progrtam must be a .csv formatted properly, or nothing.
    If the simulator is run without an argument, it runs default.csv from /io/csvs/'''
    if (len(sys.argv) >= 3):
        print("Only one or zero arguments is accepted.")
        print("If no arguments, default file is read.")
        print("If an argument is given, it should be the name of the input csv in this folder.")
        sys.exit(0)
    if (len(sys.argv) == 1):
        infile = open(os.getcwd() + '/io/csvs/default.csv', 'r')
    else:
        infile = open(sys.argv[1], 'r')
    # Read in all lines from the file, and close it
    script = infile.readlines()
    infile.close()
    # Get time interval length and BC number
    time_interval = float(script.pop(0))
    bc_num = int(script.pop(0))
    bm_num = int(script.pop(0))
    # Assign RTs until delimiter 31
    while(1):
        tmp = int(script.pop(0))
        if(tmp == 31):
            break
        elif((0 <= tmp) and (tmp <= 30)):
            if tmp not in rt_nums:
                rt_nums.append(tmp)
    # By the end, bc_num rt_nums and time_interval should all be set
    # The rest of script[] should contain only the messages portion
    return


def main():
    # Parse the .csv
    parse_csv()
    # Set up the bc, bm, and rts
    bus_controller  = bc.bc(bc_num)
    bus_monitor     = bm.bm(bm_num)
    remote_terminals = []
    for rt_num in rt_nums:
        remote_terminals.append(rt.rt(int(rt_num)))
    
    # Process the messages 
    try:
        while script.size != 0:
            # Parse command by commas into fields
            command = (script.pop(0)).split(",")
            #TODO: Figure out how to command RTs and the BC to perform the actions coded in the command
            for remote_terminal in remote_terminals:
                if(remote_terminal.return_rt_num() == int(command[0])):
                    # This RT/BC is the sender in this command
                    # Cut off field for sender # before passing
                    command.pop(0)
                    # Pass instruction to RT
                    pass

    # On Keyboard Interrupt, exit the program and deallocate memory
    except KeyboardInterrupt:
        ## TODO: Del everything we spawn
        exit()