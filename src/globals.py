import threading

local_data = dict()
current_view = list()
local_clocks = dict()
known_clocks = dict()
last_write = dict()
address = str()
node_id = int(-1) # node starts off with no ID (uninit)
shard_member = -1 # node starts off not in a shard
shard_view = dict() # holds what nodes are in what shards! 
# if you want the num of shards, take the len(globals.shard_view.keys())


syncThread = threading.Thread()
