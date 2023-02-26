from flask import Flask, request, jsonify, Blueprint
import requests
from globals import current_view, data, data_clocks, address
from broadcast import broadcast
from vector_clocks import Vector_Clock

blueprint = Blueprint('blueprint', __name__)

def in_view():
  body = request.get_json()
  source = body.get('source')
  if source not in current_view:
    return False
  return True

def quorum_rep():

  # compare vector clocks ##

  # 
  return 'hi'

@blueprint.route('kvs/data/<key>', methods = ['PUT'])
def handle_put(key):

  # get body and data
  body = request.get_json()
  client_vc = body.get('causal-metadata')
  val = body.get('val')

  # comparing vector clocks ##
  sending_vc = None
  result = data_clocks.compare(client_vc[key], val)
  if result is 1 or result is 0: # if the client's vector clock is less than or equal to self's
    sending_vc = data_clocks.get_key_clock(key)
  else: # if result is -1, ie the client's vector clock is greater than self's
    sending_vc = client_vc
    data_clocks.copy(client_vc) # set self's clock to that of the client

  # broadcast
  responses = broadcast('PUT', '/internal/write/<key>', key, data_clocks[key]) # change data_clocks[key] to the sending_vc

  # set return code
  return_code = 200 if key in data else 201

  # update kvs
  data[key] = body.get('val')

  # update vc
  data_clocks[key] += 1

  # return vc and return_code ##
  return jsonify({"causal-metadata" : data_clocks[key]}), return_code
  




@blueprint.route('/internal/write/<key>', methods = ['PUT', 'DELETE'])
def handle_rep_put(key):
  
  # recieved msg from not in view node
  if not in_view():
    return jsonify(error="uninitialized"), 418
  
  return 200
