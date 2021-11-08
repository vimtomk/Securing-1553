from encryptor import *
import string
import secrets



message = "Hello my name is Braden Willingham and I am a senior at UAH"

braden_public = 197
braden_private = 199

jenna_public = 151
jenna_private = 157

braden = DHKE(braden_public, jenna_public, braden_private)
jenna = DHKE(braden_public, jenna_public, jenna_private)



################ PARTIAL KEY CREATION ######################

## This creates the Partial key for Braden##
braden_partial = braden.generate_partial_key()
print(braden_partial)

## This creates the partial key for Jenna ##
jenna_partial = jenna.generate_partial_key()
print(jenna_partial)

############################################################


################ FULL KEY CREATION #########################

braden_full = braden.generate_full_key(jenna_partial)
print(braden_full)

jenna_full = jenna.generate_full_key(braden_partial)
print(jenna_full)

############################################################


#################### ENCRYPT MESSAGE ########################

braden_encrypted = braden.encrypt_message(message)
print(braden_encrypted)


##############################################################


##################### DECRYPT MESSAGE ########################

jenna_decrypted = jenna.decrypt_message(braden_encrypted)
print(jenna_decrypted)

##############################################################



##################### REAL EXAMPLE ############################

# create BC public/private keys
bus_controller_public_key = secrets.randbelow(256)
bus_controller_private_key = secrets.randbelow(256)

#print(bus_controller_public_key)

# create arrays to store all RT 
remote_terminals_public = []
remote_terminals_private = []

x = 0

for x in range(32):
    
    public_key_name = "remote_terminal_" + str(x) + "_public_key"
    remote_terminals_public.append(public_key_name)
    remote_terminals_public[x] = secrets.randbelow(256)

    private_key_name = "remote_terminal_" + str(x) + "_private_key"
    remote_terminals_private.append(private_key_name)
    remote_terminals_private[x] = secrets.randbelow(256)


remote_terminals_partial_keys = []
remote_terminals_full_keys = []

x = 0

for x in range(32):
    partial_key_name = "remote_terminal_" + str(x) + "_partial_key"
    remote_terminals_partial_keys.append(partial_key_name)
    #remote_terminals_partial_keys[x] = 



#Checks length of list of remote terminal public keys
#print(len(remote_terminals_public))
#print(len(remote_terminals_private))

#for loop that printed each public key for each remote terminal
#for x in range(32):
    #print(remote_terminals_public[x])    