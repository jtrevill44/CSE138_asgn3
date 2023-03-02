from flask import Blueprint, request, jsonify

from globals import *
from broadcast import broadcast
from vector_clocks import *

app = Blueprint('main', __name__)

app.route("/kvs/data/<key>", methods=["GET"])
def get(key):
    #get the json object from the request
    json = request.get_json()
    #get the metadata from the json
    causal_metadata = json.get('causal_metadata', None)
    request_clock = causal_metadata.get(key, None)
    #Request clock not existing means message isn't causally dependant on the value 
    if request_clock == None:
        #check if we've seen the key 
        if local_clocks.get(key) == None:
            #if not return an error
            return jsonify(causal_metadata=local_clocks), 404
        else:
            #if so, update the clocks to signify a read
            increment(local_clocks, key, node_id)
            tmp = broadcast('PUT','/internal/replicate', key, local_clocks[key], local_data[key])
            #and return the data
            return jsonify(val=local_data[key], causal_metadata=local_clocks)
    #compare internal clock to response clock
    #keep looping while the metadata is behind
    while(compare(local_clocks, key, causal_metadata.get(key, [0]*len(current_view)))<0):
        #if internal behind, check with other replica's for updates. 
        #either a response with the newer vector clock, or hang
        responses = broadcast("GET", "/internal/read", key, causal_metadata[key])
        #tmp variable to hold the newst list/val seen
        newest_clock = local_clocks.get(key, [0] * len(current_view))
        newest_value = local_data.get(key)
        #find most updated vector clock, and take it's value
        for r in responses:
            if(r == -1):
                continue
            json = r.json()
            if(compare(json, 'vector_clock', newest_clock)>0):
                newest_clock = json.get('vector_clock')
                newest_value = json.get('val')
        #pass
        local_clocks[key] = newest_clock
        local_data[key] = newest_value
        #update internal information
        #data_clocks.copy_key(updated_clock, key)
    #now we know our internal information is synced at least to where the client was, 
    #so everything is causally consistent. 

    increment(local_clocks, key, node_id)
    tmp = broadcast('PUT','/internal/replicate', key, local_clocks[key], local_data[key])
    #and return the data
    return jsonify(val=local_data[key], causal_metadata=local_clocks)
    #update clock to represent the successful read, and broadcast the new clock to replicas
    #broadcast(PUT, "/internal/write", key, data_clocks.get_key_clock(key))
