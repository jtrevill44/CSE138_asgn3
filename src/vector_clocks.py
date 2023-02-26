from globals import *

# function finds a node's index for vector clocks!
# returns -1 if not in view
def find_index() -> int:
    for x in range(len(current_view)):
        if current_view[x] == address:
            return x
    return -1 



class Vector_Clock:

    # hold state for index on the clock!
    # no need for input to function!


    def __init__(self) -> None:
        self.clock = dict() # init to an empty clock
        self.index = find_index() 

    def add_key(self, key: str):
        self.clock[key] = [0] * len(current_view)
        return

    # sets entire clock (all keys) to another clock (all keys)
    def copy(self, other_clock_all: dict):
        self.clock = other_clock_all
        return
    
    # sets the clock at key to the clock passed in
    def copy_key(self, key:str, other_clock: list):
        self.clock[key] = other_clock
        return

    def reset (self): # clears the clock!
        self.clock.clear()
        return

    def increment(self, key: str): # index is the index of your number in the VC
        self.clock[key][self.index] += 1
        return
    
    # returns the value of the whole clock.
    # primarily used for catching a node up!
    def get_clock(self) -> dict:
        return self.clock
    
    # returns the clock for one key
    def get_key_clock(self, key: str) -> list:
        return self.clock[key]


    #                       PLEASE NOTE:
    #   this function does not take in another Vector_Clock object
    #   when using this function please pass the list (the actual clock)
    #   of clock you would like to compare it to. I made it this way
    #   because when we recieve a clock from a message, we don't 
    #   wanna have to package it into a object. instead we can just 
    #   use the list that was given to us in the message.
    def compare(self, other_clock: list, key: str) -> int:
    # function compares the vector clocks of two clocks
    # input: list representing the clock of another,
    #        a key for the clock you wish to compare
    #
    # output: 1 if self is greater than other clock,
    #         0 if concurrent
    #         -1 if self is less than other clock
    #         2 if equal

        GREATER_THAN = 1
        LESS_THAN = -1
        CONCURRENT = 0
        EQUAL_TO = 2

        less_val_found = False
        greater_val_found = False

        clock_check = self.clock[key]

        for i in range(len(clock_check)):
            if clock_check[i] > other_clock[i]:
                greater_val_found = True
            elif clock_check[i] < other_clock[i]:
                less_val_found = True
            else:
                continue
        
        if greater_val_found and not less_val_found:
            return GREATER_THAN
        elif less_val_found and not greater_val_found:
            return LESS_THAN
        elif less_val_found and greater_val_found:
            return CONCURRENT
        else:
            return EQUAL_TO

