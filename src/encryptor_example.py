#!/usr/bin/python3

import bus
import bc, rt, bm, os, sys, threading, time
from encryptor import DHKE

# Initialize BC
bus_controller  = bc.bc(0, [1]) # BC at terminal 0 and 1 RT at terminal 1

# Initialize RT
remote_terminal = rt.rt(1)  #Initialize one RT with its number being 1

# Initialize Bus
databus = bus()

# Loop here and try-catch
def main(self):
        
    while(1):
        try:
           # Send public key to RT 1 and sleep for 1 second
           bus_controller.send_public_key()
           time.sleep(1)

           
           # If RT receives the key successfully it should be able to print out the BC's public key 
           print(rt.BC_public_key)

           # BC should now send a command word to RT 1 asking for its public key
           bus_controller.receive_public_key()

           # If BC receives the key successfully then we should be able to print out the RT's public key
           print(bus_controller.RT_keys[1])

           # Create an instance of DHKE for the BC and RT
           bus_controller_ep = DHKE(bus_controller.public_key, remote_terminal.public_key, bus_controller.private_key)
           remote_terminal_ep = DHKE(remote_terminal.public_key, bus_controller.public_key, remote_terminal.private_key)
           

           #Create partial key and full key for each device respectfully
           bus_controller_ep.generate_partial_key()
           bus_controller_ep.generate_full_key()

           remote_terminal_ep.generate_partial_key()
           remote_terminal_ep.generate_full_key()

           # Example Message that will be encrypted on the BC side and decrypted on the RT side 
           # Print message before encryption process for proof of concept
           message = "Hello"
           print(message)

           # Create the encrypted message on BC side by using the encrypt message function from DHKE class
           encrypted_message = bus_controller_ep.encrypt_message(message)
           
           # This function will get the size of the message in bytes
           size = sys.getsizeof(encrypted_message)

           # Find the amount of bits we need to encode all the bytes
           # Even number of bytes
           if (size % 2 == 0):
               data_word_bits_needed = (size / 2) * 16 
           # Odd number of bytes
           else:
               data_word_bits_needed = ((size / 2) + 1) * 16

           # List to store data word list
           ## TODO: Finish
           for i in range(0, data_word_bits_needed):
               pass



        except KeyboardInterrupt:
            self.__del__()
            print("\nSimulation has shutdown and cleaned up.")
            exit()
        return


