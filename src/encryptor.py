#!/usr/bin/python3



class DHKE(object):
    
    def __init__(self, public_key1, public_key2, private_key):
        self.public_key1 = public_key1
        self.public_key2 = public_key2
        self.private_key = private_key
        self.full_key = None


    def generate_partial_key(self):
        partial_key = self.public_key1 ** self.private_key
        partial_key = partial_key % self.public_key2 
        return partial_key


    def generate_full_key(self, partial_key):
        full_key = partial_key ** self.private_key     
        full_key = full_key % self.public_key2   
        self.full_key = full_key
        if self.full_key == 0:
            self.full_key += 5
        return full_key


    def encrypt_message(self,message):
        encrypted_message = ""
        key = self.full_key
        for c in message:
            encrypted_message += chr(ord(c)+key)
        return encrypted_message


    def decrypt_message(self, encrypted_message):
        decrypted_message = ""
        key = self.full_key
        for c in encrypted_message:
                decrypted_message += chr(ord(c)-key)
        return decrypted_message
        