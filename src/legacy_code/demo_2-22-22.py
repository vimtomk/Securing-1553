#!/usr/bin/env python3

# This code serves to demonstrate the capabilities of the MIL-STD-1553 
# Emulator for the 2/22/2022 Instructor Meeting
from rt   import rt
from bc   import bc
from bus  import bus
from bitstring import BitArray
from time import sleep


class demo():

    # Initialization function
    def __init__(self):
        print("----Initializing Bus----")
        self.databus = bus()
        print("Bus Init Successful.")

        if(self.databus.is_empty()):
            print("Current bus status is : Empty")
        else:
            print("Current bus status is : In Use")

        # Setup RT objects and pass them along to the BC
        print("\n----Initializing RTs----")
        self.rt_nums = [1,2,3,4,5]
        self.rts     = []
        for rt_num in self.rt_nums:
            self.rts.append(rt(rt_num))
        
        # Setup BC
        self.bc_num         = 0
        self.bus_controller = bc(0, self.rts)
        print("Bus controller has been initialized.")

        # Begin sending messages using BC/RT Functions and having the recipient print message type and contents.
        self.main()

    
    # Delete Function
    def __del__(self):
        del(self)

    # Loop here and try-catch
    def main(self):
        # Do logic
        #data_hi = "0100100001101001" # Ascii 8 bit binary for the string "Hi"
        while(1):
            try:
                # Send message to RT 1 to transmit
                for rt in self.rts:
                    tmp_msg = self.bus_controller.create_command_word(rt.num.int, 1, 1, 1)
                    print("Bus Controller sent msg: 0x{}".format(tmp_msg.hex))
                    self.bus_controller.issue_command_word(tmp_msg)
                    #data = self.databus.read_BitArray()
                    #print("0x{}".format(data.hex))
                    rt.read_message_timer(1)
                    sleep(0.5)
                sleep(0.5)
                self.rts[0].databus.write_BitArray(BitArray("0b11001001000011010011"))
                print("RT" + str(self.rts[0].return_rt_num().int) + " sent the message \"Hi\" as a data word!")
                sleep(1)
                self.rts[1].read_message_timer(0)
                sleep(5)
                pass

            except KeyboardInterrupt:
                self.__del__()
                print("\nSimulation has shutdown and cleaned up.")
                exit()
        return

d = demo()
