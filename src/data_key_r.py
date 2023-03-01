from flask import Blueprint, request

from globals import *
from broadcast import broadcast

app = Blueprint('main', __name__)

app.route("/kvs/data/<key>", methods=["GET"])
def get(key):
    #get the json object from the request
    json = request.get_json()
    #get the metadata from the json
    causal_metadata = json.get('causal_metadata', None)
    #compare internal clock to response clock
    if(data_clocks.compare(causal_metadata[key], key) < 0):
        #keep looping while the metadata is behind
        while(data_clocks.compare(causal_metadata[key], key) < 0):
            #if internal behind, check with other replica's for updates. 
            #either a response with the newer vector clock, or hang
            responses= broadcast("GET", "/internal/read", key, causal_metadata[key])
            #find most updated vector clock, and take it's value
            pass
        #update internal information
        #data_clocks.copy_key(updated_clock, key)
    #now we know our internal information is synced at least to where the client was, 
    #so everything is causally consistent. 

    #update clock to represent the successful read, and broadcast the new clock to replicas
    data_clocks.increment(key, node_id)
    #broadcast(PUT, "/internal/write", key, data_clocks.get_key_clock(key))
    return data[key]
