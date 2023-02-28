from globals import *


class Vector_Clock:

    # hold state for index on the clock!
    # no need for input to function!


    def __init__(self) -> None:
        self.clock = dict() # init to an empty clock

    def add_key(self, key: str) -> None:
        self.clock[key] = [0] * len(current_view)
        return

    # sets entire clock (all keys) to another clock (all keys)
    def copy(self, other_clock_all: dict) -> None:
        self.clock = other_clock_all
        return
    
    # sets the clock at key to the clock passed in
    def copy_key(self, key:str, other_clock: list) -> None:
        self.clock[key] = other_clock
        return

    def reset (self) -> None: # clears the clock! 
        self.clock.clear()
        return

    def increment(self, key: str, index: int ) -> None: # index is the index of your number in the VC
        self.clock[key][index] += 1
        return

    def combine(self, key: str, other_clock: list) -> None:
        for index in range(len(self.clock[key])):
            self.clock[key][index] = max(self.clock[key][index], other_clock[index])
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

        if not other_clock: # other_clock is empty
            return GREATER_THAN

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

