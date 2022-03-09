#!/usr/bin/env python3

# This file is supposed to be used to actively test new developments in the simulator

from bus import bus
import bc, rt, bm, os, sys, threading

databus = bus()
bc_num        = 0
bm_num        = 0
rt_nums       = []
time_interval = 0
script        = []

def parse_csv():
    '''Parses out a .csv file into the initialization parameters and action script.
    The argument for the progrtam must be a .csv formatted properly, or nothing.
    If the simulator is run without an argument, it runs a default script from /io/csvs/default.csv'''
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
    parse_csv()

    bus_monitor      = bm.bm(bm_num)
    
    remote_terminals = []
    for rt_num in rt_nums:
        remote_terminals.append(rt.rt(int(rt_num)))
    
    bus_controller = bc.bc(bc_num, remote_terminals)