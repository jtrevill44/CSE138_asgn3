local_data = dict()
current_view = list()
local_clocks = dict()
last_write = dict()
address = str()
node_id = int(-1) # node starts off with no ID (uninit)


def learn_new_keys(my_clock: dict, causal_data: dict) -> None:
    new_keys = [x for x in causal_data.keys() if x not in my_clock.keys()]
    for key in new_keys:
        my_clock[key] = causal_data[key]
    return;