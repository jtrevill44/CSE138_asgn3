from flask import Flask, request, jsonify, Blueprint
import requests
from globals import current_view, data, data_clocks, address
from broadcast import broadcast

blueprint = Blueprint('blueprint', __name__)

def in_view(): ## figure out how to implement this
  body = request.get_json()
  source = body.get('source')
  if source not in current_view:
    return False
  return True

def quorum_rep():
  # figure out how to check if the sender is in the view ##

  # compare vector clocks ##

  # 
  return 'hi'

@blueprint.route('kvs/data/<key>', methods = ['PUT'])
def handle_put(key):

  # comparing vector clocks ##

  # initialize sending_vc
  body = request.get_json()
  client_vc = body.get('causal-metadata')
  # compare client_vc with node vc, take the latest FF

  # broadcast
  responses = broadcast('PUT', '/internal/write/<key>', key, data_clocks[key]) # change data_clocks[key] to the sending_vc

  # set return code
  return_code = 200 if key in data else 201

  # update kvs
  data[key] = body.get('val')

  # update vc

  # return vc and return_code ##
  




@blueprint.route('/internal/write/<key>', methods = ['PUT', 'DELETE'])
def handle_rep_put(key):
  if not in_view():
    return jsonify(error="uninitialized"), 418
  
  return 200
