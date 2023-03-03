from flask import Blueprint, request, jsonify

from globals import *
from broadcast import broadcast
from vector_clocks import compare

app = Blueprint(__name__, "__main__")

@app.route('/data/kvs', methods=['GET'])
def kvs():
    #get the data from the request
    request_json = request.get_json()
    causal_metadata = request_json.get('causal_metadata', None)
    update_known_clocks(causal_metadata)
    #loop til we're up to date with the request's clocks
    while(True):
        #get the info from all the other nodes
        datas = broadcast('GET', '/internal/kvs', '',[], '')
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
            for key, value in kvs_data:
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
    return jsonify(count=len(local_clocks), keys=local_data.keys(), causal_metadata=known_clocks) 
