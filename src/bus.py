#!/usr/bin/env python3


import queue

# This class acts as a queue of messages, which is how data would be
# handled on a bus.
class Bus:

    # Initialize the queue "messages"
    def __init__(self):
        self.messages = queue.Queue()

    # Return the queue as a list. This is helpful for when you want
    # to read something from the queue without removing an element.
    def to_list(self):
        return list(self.messages.queue)
    
    # Adds (push) a message to the queue and to the "BM"
    def add_message(self, msg):
        self.messages.put(msg)
    
    # Returns (pops) a message from the queue
    def return_message(self):
        return self.messages.get()

    # Return first message without popping
    def return_first_message(self):
        return(self.messages.queue[0])

    # Takes in a list as what is on the bus(enables MITM)
    def mitm_message(self, lst):
        # Clear the message queue and replace with provided list
        self.messages.queue.clear()
        [self.messages.put(msg) for msg in lst]
    
    # Returns bool if bus is empty. Good for error handling in other
    # programs.
    def is_empty(self):
        return self.messages.empty()

    # Clear all messages on bus
    def clear_all(self):
        self.messages.queue.clear()

    # Delete the instance for good memory management.
    def __del__(self):
        del(self)

# Create instance of Bus to use throughout the program
databus = Bus()