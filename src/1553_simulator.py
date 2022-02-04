#!/usr/bin/env python3

from bus import bus
import bc, rt, bm, os, sys

databus = bus()     # Points to the shared bus
bc_num  = 0         # Termianal Number of the BC
rt_count = 0        # Number of RTs to initialize
time_interval = 0
script = []

def parse_csv():
    '''Parses out a .csv file into the interval, rt count, and action script.
    The argument must be 
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
    script = infile.readlines() #TODO: Replace this with reading csv line-by-line into linked list or queue
    infile.close()

    return


def main():
    # Set up the bus
    parse_csv()
    # Run everything in try until interrupted by keyboard interrupt signal
    try:
        pass
    
    # On Keyboard Interrupt, exit the program and deallocate memory
    except KeyboardInterrupt:
        ## TODO: Del everything we spawn
        exit()