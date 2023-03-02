from flask import Flask, request, jsonify, Blueprint
import requests
import globals
from broadcast import broadcast
from vector_clocks import *

blueprint = Blueprint('blueprint', __name__)
EIGHT_MEGABYTES = 8388608

@blueprint.route('kvs/data/<key>', methods = ['PUT'])
def handle_put(key):

  # get body and data
  body = request.get_json()
  client_vc = dict(body.get('causal-metadata'))
  val = body.get('val')

  if len(val) > EIGHT_MEGABYTES:
    return jsonify(error="val too large"), 400


  # set return code
  return_code = 200 if key in globals.local_data else 201
  # update kvs
  globals.local_data[key] = val


  # comparing vector clocks ##
  result = compare(globals.local_clocks, key, client_vc.get(key, []))
  if result is 0:
    combine(globals.local_data, key, client_vc.get(key, []))
  elif result is -1: # if result is -1, ie the client's vector clock is greater than self's
    copy_key(globals.local_clocks, key, client_vc[key]) # set self's clock to that of the client

  # update vc
  if key not in globals.local_clocks.keys(): # we need a new entry in the clocks
    add_key(globals.local_clocks, key)

  increment(globals.local_data, key, globals.node_id)

  # broadcast
  responses = broadcast('PUT', '/internal/write/<key>', key, globals.local_clocks[key]) # change data_clocks[key] to the sending_vc

  return jsonify({"causal-metadata" : globals.local_clocks}), return_code

  # return vc and return_code ##
  

