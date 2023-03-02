from flask import Flask, request, jsonify, Blueprint
import requests
import globals
from broadcast import broadcast
from vector_clocks import *

blueprint = Blueprint('blueprint', __name__)
EIGHT_MEGABYTES = 8388608

@blueprint.route('kvs/data/<key>', methods = ['PUT', 'DELETE'])
def handle_put(key):

  # get body and data
  body = request.get_json()
  client_vc = dict(body.get('causal-metadata'))
  val = body.get('val')
  learn_new_keys(globals.local_clocks, client_vc) # find key clocks we don't know of

  if len(val) > EIGHT_MEGABYTES:
    return jsonify(error="val too large"), 400

  return_code = 200 if key in globals.local_data else 201

  # comparing vector clocks ##
  result = compare(globals.local_clocks, key, client_vc.get(key, []))
  if result is 0:
    combine(globals.local_data, key, client_vc.get(key, []))
  elif result is -1: # if result is -1, ie the client's vector clock is greater than self's
    copy_key(globals.local_clocks, key, client_vc[key]) # set self's clock to that of the client
  elif result is 1: # we were in the future, don't do anything and send our clock.
    return jsonify({"causal-metadata" : globals.local_clocks}), return_code

  # update vc
  if key not in globals.local_clocks.keys(): # we need a new entry in the clocks
    add_key(globals.local_clocks, key)

  increment(globals.local_data, key, globals.node_id)

  # broadcast
  responses = broadcast(request.method, f'/internal/write/<{key}>', key, globals.local_clocks, val=val) # change data_clocks[key] to the sending_vc

  return jsonify({"causal-metadata" : globals.local_clocks}), return_code

  # return vc and return_code ##
  

