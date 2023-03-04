from flask import Blueprint, request, jsonify
from vector_clocks import *
from globals import *
from broadcast import broadcast
from vector_clocks import compare
import asyncio

get_all = Blueprint("get_all", __name__)

@get_all.route('/kvs/data', methods=['GET'])
def kvs():
    if (globals.node_id == -1):
      return jsonify({"causal-metadata" : causal_metadata, 'error' : 'uninitialized'}), 418

    #get the data from the request
    request_json = request.get_json()
    causal_metadata = request_json.get('causal_metadata', None)
    if causal_metadata != None:
        update_known_clocks(causal_metadata)
    else:
        causal_metadata = dict()
    #loop til we're up to date with the request's clocks
    while(True):
        #get the info from all the other nodes
        datas = asyncio.run(broadcast('GET', '/kvs/internal/kvs', '',[], ''))
        #loop through the responses 
        for data in datas:
            #if dead, skip
            if data == -1:
                continue
            #get the data from the responses
            json = data.json()
            clocks = json.get('vector_clock')
            kvs_data = json.get('kvs')
            #compare all their data against ours, if theirs is ahead, update to it
            for key, value in kvs_data.items():
                if compare(local_clocks, key, clocks.get(key, [0] * len(current_view))) < 0:
                    local_clocks[key] = clocks.get(key)
                    local_data[key] = kvs_data.get(key)
        #check if we're behind the request at all
        behind = False
        for key, value in causal_metadata:
           if compare(local_clocks, key, value) < 0:
               behind = True
        #if behind is True, at least one of our clocks is behind the requests
        #if behind is False, then all of our local info is caught up with the requests data
        if not behind:
            break
        
    #return keys of all data
    return jsonify({"count" : len(local_clocks), "keys" : list(local_data.keys()), "causal-metadata" : known_clocks}), 200
