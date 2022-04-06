#!/usr/bin/python3
from bus import bus
import bc, rt, bm, os, sys, threading, time, message
from encryptor import DHKE
import pdb
import sys



sys.setrecursionlimit(100000000)


# Loop here and try-catch
def main():


    # Initialize Bus
    databus = bus()   

    rt_nums = [1,2]
    
    # Initialize BC
    # Getting stuck here, start here and fix this
    bus_controller  = bc.bc(0, rt_nums) # BC at terminal 0 and 1 RT at terminal 1
    print("Hi")

    # Initialize RT
    remote_terminal = rt.rt(1)  #Initialize one RT with its number being 1
 

    


    
    while(1):
        try:

            
                     
            # Send public key to RT 1 and sleep for 1 second
            bus_controller.send_public_key()
            time.sleep(1)

           
            # If RT receives the key successfully it should be able to print out the BC's public key 
            print(remote_terminal.BC_public_key)

            # BC should now send a command word to RT 1 asking for its public key
            bus_controller.receive_public_key()

            # If BC receives the key successfully then we should be able to print out the RT's public key
            print(bus_controller.RT_keys[1])
            

            # Create an instance of DHKE for the BC and RT
            bus_controller_ep = DHKE(bus_controller.public_key, remote_terminal.public_key, bus_controller.private_key)
            remote_terminal_ep = DHKE(remote_terminal.public_key, bus_controller.public_key, remote_terminal.private_key)
            
            print("Bus Controller Public Key: " + str(bus_controller.public_key))
            print("Remote Terminal Public Key: " + str(remote_terminal.public_key))



            #Create partial key and full key for each device respectfully
            bus_controller_ep.generate_partial_key()
            bus_controller_ep.generate_full_key()

            print(bus_controller_ep.full_key)

            remote_terminal_ep.generate_partial_key()
            remote_terminal_ep.generate_full_key()

            # Example Message that will be encrypted on the BC side and decrypted on the RT side 
            # Print message before encryption process for proof of concept
            message = "Hello"
            print(message)

            # Create the encrypted message on BC side by using the encrypt message function from DHKE class
            encrypted_message = bus_controller_ep.encrypt_message(message)
           
            # Perform BC to RT Transfer with the encrypted message created
            # Allow RT to be able to receive data sent on the bus
            bus_controller.BC_RT_Transfer(1, encrypted_message)
           

            
     
            
     
     
        except KeyboardInterrupt:
        #    self.__del__()
        #    print("\nSimulation has shutdown and cleaned up.")
             exit()
        return

main()