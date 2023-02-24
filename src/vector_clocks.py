from globals import *

class Vector_Clock:

    def __init__(self) -> None:
        self.clock = dict() # init to an empty clock

    def add_key(self, key: str, num_of_nodes: int):
        self.clock[key] = [0] * num_of_nodes
        return

    def copy(self, other_clock: dict):
        self.clock = other_clock
        return

    def reset (self): # clears the clock!
        self.clock.clear()
        return

    def increment(self, index: int, key: str): # index is the index of your number in the VC
        self.clock[key][index] += 1
        return
    
    # returns the value at
    def get_clock(self) -> dict:
        return self.clock

    # functions compares the vector clocks of two clocks
    # input: list representing the clock of another 
    def compare(self, other: list, key: str) -> int:
        

