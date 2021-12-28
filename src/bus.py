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
        tmp = list(self.messages.queue)
        return tmp
    
    # Adds (push) a message to the queue
    def add_message(self, msg):
        self.messages.put(msg)
    
    # Returns (pops) a message from the queue
    def return_message(self):
        tmp = self.messages.get()
        return tmp
    
    # Returns bool if bus is empty. Good for error handling in other
    # programs.
    def is_empty(self):
        return self.messages.empty()
            
    # Delete the instance for good memory management.
    def __del__(self):
        del(self)
