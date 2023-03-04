from flask import Flask, request, jsonify, Blueprint
import requests
import globals
from broadcast import broadcast
from vector_clocks import *
import asyncio

client_side = Blueprint('client_side', __name__, url_prefix= '/kvs/data')
EIGHT_MEGABYTES = 8388608

@client_side.route('/<key>', methods = ['PUT', 'DELETE'])
def handle_put(key):
  if (len(request.url) > 2048):
     return jsonify(error='URL is too large'), 414

  # get body and data
  body = request.get_json()

  causal_metadata = body.get('causal-metadata', None)
  if causal_metadata is not None:
    update_known_clocks(causal_metadata)
    request_clock = causal_metadata.get(key, None)
  else:
    causal_metadata = dict()
    request_clock = None
  val = body.get('val')

  if (globals.node_id == -1):
      return jsonify({"causal-metadata" : causal_metadata, 'error' : 'uninitialized'}), 418

  if request.method == 'PUT':
    if len(val) > EIGHT_MEGABYTES:
      return jsonify(error="val too large"), 400
    if val is None:
      return jsonify(error="bad request"), 400

  return_code = 200 if key in globals.local_data else 201

  if key not in globals.local_clocks.keys():
    add_key(globals.local_clocks, key)
  if key not in globals.known_clocks.keys():
    add_key(globals.known_clocks, key)

  # comparing vector clocks ##
  result = compare(globals.local_clocks, key, causal_metadata.get(key, [0] * len(globals.current_view)))
  if result == 0:
    combine(globals.local_data, key, causal_metadata.get(key, []))
  elif result == -1: # if result is -1, ie the client's vector clock is greater than self's
    copy_key(globals.local_clocks, key, causal_metadata[key]) # set self's clock to that of the client

  # update vc

  increment(globals.local_clocks, key, globals.node_id)
  increment(globals.known_clocks, key, globals.node_id)
  # broadcast
  responses = asyncio.run(broadcast(request.method, f'/kvs/internal/replicate/{key}', key, globals.local_clocks, val=val, source=globals.address, node_id=globals.node_id)) # change data_clocks[key] to the sending_vc

  return jsonify({"causal-metadata" : globals.known_clocks}), return_code

  # return vc and return_code ##
  

@client_side.route("/<key>", methods=["GET"])
def get(key):

    #get the json object from the request
    json = request.get_json()

    #get the metadata from the json
    temp = json.get('causal-metadata', None)
    if temp is not None:
      causal_metadata = dict(json.get('causal-metadata', None))
      update_known_clocks(causal_metadata)
      request_clock = causal_metadata.get(key, None)
    else:
       causal_metadata = dict()
       request_clock = list()

    if (globals.node_id == -1):
      return jsonify({"causal-metadata" : causal_metadata, 'error' : 'uninitialized'}), 418

    #Request clock not existing means message isn't causally dependant on the value 
    if request_clock == None:
        #check if we've seen the key 
        if globals.known_clocks.get(key) == None:
            #if not return an error
            return jsonify({"causal-metadata" : globals.known_clocks}), 404
        elif compare(globals.local_clocks, key, globals.known_clocks.get(key)) == 2:
            if globals.local_data.get(key, None) is None:
              return {"causal-metadata": globals.known_clocks}, 404
            return jsonify({"val" : globals.local_data[key], "causal-metadata" : globals.known_clocks})
        
    #compare internal clock to response clock
    #keep looping while the metadata is behind
    while(compare(globals.local_clocks, key, causal_metadata.get(key, [0]*len(globals.current_view)))<=0):
        #if internal behind, check with other replica's for updates. 
        #either a response with the newer vector clock, or hang
        responses = asyncio.run(broadcast("GET", "/internal/read", key, causal_metadata[key]))
        #tmp variable to hold the newst list/val seen
        newest_clock = globals.local_clocks.get(key, [0] * len(globals.current_view))
        newest_value = globals.local_data.get(key)
        #find most updated vector clock, and take it's value
        for r in responses:
            if(r == -1):
                continue
            json = r.json()
            if(compare(json, 'vector_clock', newest_clock)>0):
                newest_clock = json.get('vector_clock')
                newest_value = json.get('val')
        #update internal information
        globals.local_clocks[key] = newest_clock
        globals.local_data[key] = newest_value
    #now we know our internal information is synced at least to where the client was, 
    #so everything is causally consistent. 


    #and return the data
    if globals.local_data.get(key, None) is None:
      return {"causal-metadata": globals.known_clocks}, 404
    return jsonify({"val" : globals.local_data[key], "causal-metadata" : globals.known_clocks})
