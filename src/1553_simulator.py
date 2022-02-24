#!/usr/bin/env python3

from bus import bus
import bc, rt, bm, os, sys, threading#, time

databus = bus()     # Points to the shared bus
bc_num  = 0         # Terminal Number of the BC
bm_num  = 0         # Terminal Number of the BM
rt_nums = []        # List of RT numbers
time_interval = 0   # How long, in seconds, each time interval should be
script = []         # Queue of information from input .csv

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
    # Parse the .csv
    parse_csv()
    # Set up the bc, bm, and rts
    bus_monitor     = bm.bm(bm_num)
    remote_terminals = []
    for rt_num in rt_nums:
        remote_terminals.append(rt.rt(int(rt_num)))
    bus_controller  = bc.bc(bc_num, remote_terminals) # Bus controller is passed a list of pointers to all RT instances
    
    # Set everything to begin listening in periodically at the same time interval
    threading.Timer(time_interval, bus_controller.read_message_timer(time_interval)).start
    threading.Timer(time_interval, bus_monitor.record_bus_contents(time_interval)).start
    for remote_terminal in remote_terminals:
        threading.Timer(time_interval, remote_terminal.read_message_timer(time_interval)).start

    # Process the messages
    try:
        while(script.size != 0):
            #time.wait(time_interval) # Trickles out commands so they are not all sent at once
            # Parse command by commas into fields
            command = (script.pop(0)).split(",")
            if(bus_controller.return_terminal_num() < 10):
                ph = "0" + str(bus_controller.return_terminal_num())
            else:
                ph = str(bus_controller.return_terminal_num())
            # Check if the BC needs to process this command
            if( ph == command[0][2:]):
                # The BC is meant to process this command
                bus_controller.queue_message(command)
            # Check if any RT needs to process this command
            for terminal in remote_terminals:
                if(ph == command[0][2:]):
                    # This RT/BC is the sender in this command
                    # Pass instruction to RT
                    terminal.queue_message(command)
                    # Pass a copy of the event to BC
                    bus_controller.queue_message(command)

    # On Keyboard Interrupt, exit the program and deallocate memory
    except KeyboardInterrupt:
        ## TODO: Del everything we spawn
        exit()