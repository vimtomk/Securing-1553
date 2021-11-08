#!/usr/bin/python3

# This file sends some messages across the bus at some staggered times, used to debug the Logger.py program.

from Bus_Controller.BC_Simulator import Bus_Controller
from Remote_Terminal.RT_Simulator import Remote_Terminal

import threading
import time

global bc_listener_thread
global rt_listener_thread

if __name__ == "__main__":
    try:
        
        # Message 1, the default message from Simulator.py
        Bus_Controller().send_data_to_rt("01", "11", "Some Message")
        Bus_Controller().receive_data_from_rt("01", "01", "07")
        
        time.sleep(5)
        
        # Message 2
        Bus_Controller().send_data_to_rt("01", "11", "Eat my shorts!")
        Bus_Controller().receive_data_from_rt("01", "01", "08")
        
        time.sleep(5)
        
        # Message 2
        Bus_Controller().send_data_to_rt("01", "11", "Another Message.")
        Bus_Controller().receive_data_from_rt("01", "01", "09")
        
    except KeyboardInterrupt:
        exit()