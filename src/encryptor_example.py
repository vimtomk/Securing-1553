#!/usr/bin/python3

from encryptor import *
import string
import secrets

KEY = 25



#message = "Hello my name is Braden Willingham and I am a senior at UAH"

#braden_public = 197
#braden_private = 199

#jenna_public = 151
#jenna_private = 157

#braden = DHKE(braden_public, jenna_public, braden_private)
#jenna = DHKE(braden_public, jenna_public, jenna_private)



################ PARTIAL KEY CREATION ######################

## This creates the Partial key for Braden##
#braden_partial = braden.generate_partial_key()
#print(braden_partial)

## This creates the partial key for Jenna ##
#jenna_partial = jenna.generate_partial_key()
#print(jenna_partial)

############################################################


################ FULL KEY CREATION #########################

#braden_full = braden.generate_full_key(jenna_partial)
#print(braden_full)

#jenna_full = jenna.generate_full_key(braden_partial)
#print(jenna_full)

############################################################


#################### ENCRYPT MESSAGE ########################

#braden_encrypted = braden.encrypt_message(message)
#print(braden_encrypted)


##############################################################


##################### DECRYPT MESSAGE ########################

#jenna_decrypted = jenna.decrypt_message(braden_encrypted)
#print(jenna_decrypted)

##############################################################



##################### REAL EXAMPLE ############################

# create BC public/private keys
bus_controller_public_key = secrets.randbelow(KEY)
while bus_controller_public_key == 0 or bus_controller_public_key == 1:
    bus_controller_public_key = secrets.randbelow(KEY)

#print("Bus controller public key: " + str(bus_controller_public_key))

bus_controller_private_key = secrets.randbelow(KEY)
while bus_controller_private_key == 0 or bus_controller_private_key == 1:
    bus_controller_private_key = secrets.randbelow(KEY)

#print("Bus controller private key: " + str(bus_controller_private_key))

# create arrays to store all RT keys
remote_terminals_public = []
remote_terminals_private = []

x = 0

for x in range(32):
    
    public_key_name = "remote_terminal_" + str(x) + "_public_key"
    remote_terminals_public.append(public_key_name) 
    remote_terminals_public[x] = secrets.randbelow(KEY)
    while remote_terminals_public[x] == 0 or remote_terminals_public[x] == 1:
        remote_terminals_public[x] = secrets.randbelow(KEY)

    
    private_key_name = "remote_terminal_" + str(x) + "_private_key"
    remote_terminals_private.append(private_key_name)
    remote_terminals_private[x] = secrets.randbelow(KEY)
    while remote_terminals_private[x] == 0 or remote_terminals_private == 1:
        remote_terminals_private[x] = secrets.randbelow(KEY)

#print("Remote Terminal 0 public key: " + str(remote_terminals_public[0]))
#print("Remote Terminal 0 private key: " + str(remote_terminals_private[0]))



############################################################################################################################################


bus_controller_to_remote_terminals = []

x = 0

for x in range(32):

    
    bus_controller_to_remote_terminals.append(DHKE(bus_controller_public_key, remote_terminals_public[x], bus_controller_private_key))




#Create Partial keys for BC -> RT_X

x = 0

bus_controller_to_remote_terminals_partial_keys = []

for x in range(32):

    this = bus_controller_to_remote_terminals[x]
    partial_key = this.generate_partial_key()
    bus_controller_to_remote_terminals_partial_keys.append(partial_key)

#print(bus_controller_to_remote_terminals_partial_keys[0])




###################################################################################################################################################


remote_terminals_to_bus_controller = []

x = 0 

for x in range(32):

    remote_terminals_to_bus_controller.append(DHKE(bus_controller_public_key, remote_terminals_public[x], remote_terminals_private[x]))


#Create Partial keys for RT_X -> BC

x = 0

remote_terminals_to_bus_controller_partial_keys = []

for x in range(32):

    this = remote_terminals_to_bus_controller[x]
    partial_key = this.generate_partial_key()
    remote_terminals_to_bus_controller_partial_keys.append(partial_key)

#print(remote_terminals_to_bus_controller_partial_keys[0])

#Create Full Keys for BC -> RT_X

x = 0

bus_controller_to_remote_terminals_full_keys = []

for x in range(32):

    this = bus_controller_to_remote_terminals[x]
    full_key = this.generate_full_key(remote_terminals_to_bus_controller_partial_keys[x])
    bus_controller_to_remote_terminals_full_keys.append(full_key)

#print(bus_controller_to_remote_terminals_full_keys[0])
    

#Create Full Keys for RT_X -> BC 

x = 0

remote_terminals_to_bus_controller_full_keys = []

for x in range(32):

    this = remote_terminals_to_bus_controller[x]
    full_key = this.generate_full_key(bus_controller_to_remote_terminals_partial_keys[x])
    remote_terminals_to_bus_controller_full_keys.append(full_key)

#print(remote_terminals_to_bus_controller_full_keys[0])


###########################################################################################################################################################


# We will now simulate sending a message between BC and Remote Terminal 0

#message = "Hello I am the Bus Controller speaking to Remote Terminal 0"

#bus_controller_encrypted = bus_controller_to_remote_terminals[0].encrypt_message(message)

#print(bus_controller_encrypted)
#bus_controller_decrypted = remote_terminals_to_bus_controller[0].decrypt_message(bus_controller_encrypted)

#print(bus_controller_decrypted)

#message_2 = "Hello I am Remote Terminal 0 and I received your message"

#print(remote_terminals_to_bus_controller[0].full_key)
#print(bus_controller_to_remote_terminals[0].full_key)

#remote_terminal_encrypted = remote_terminals_to_bus_controller[0].encrypt_message(message_2)

#remote_terminal_decrypted = bus_controller_to_remote_terminals[0].decrypt_message(remote_terminal_encrypted)

#print(remote_terminal_encrypted)

#print(remote_terminal_decrypted)

