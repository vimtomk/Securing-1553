from encryptor import *
import string
import secrets



message = "Hello my name is Braden Willingham and I am a senior at UAH"

braden_public = 123
braden_private = 165

jenna_public = 154
jenna_private = 901

braden = DHKE(braden_public, jenna_public, braden_private)
jenna = DHKE(jenna_public, braden_public, jenna_private)



################ PARTIAL KEY CREATION ######################

## This creates the Partial key for Braden##
braden_partial = braden.generate_partial_key()
print(braden_partial)

## This creates the partial key for Jenna ##
jenna_partial = jenna.generate_partial_key()
print(jenna_partial)

############################################################


################ FULL KEY CREATION #########################

braden_full = braden.generate_full_key(braden_partial)
print(braden_full)

jenna_full = jenna.generate_full_key(jenna_partial)
print(jenna_full)

############################################################


#################### ENCRYPT MESSAGE ########################

braden_encrypted = braden.encrypt_message(message)
print(braden_encrypted)


##############################################################


##################### DECRYPT MESSAGE ########################

braden_decrypted = braden.decrypt_message(braden_encrypted)
print(braden_decrypted)

##############################################################