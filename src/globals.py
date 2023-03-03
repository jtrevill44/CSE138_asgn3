from vector_clocks import compare, combine

local_data = dict()
current_view = list()
local_clocks = dict()
known_clocks = dict()
last_write = dict()
address = str()
node_id = int(-1) # node starts off with no ID (uninit)

def update_known_clocks(causal_metadata):
    for key, clock in causal_metadata:
        if key not in known_clocks:
            known_clocks[key] = clock
        else:
            combine(known_clocks, key, clock)
