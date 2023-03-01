from flask import Flask, request, jsonify, Blueprint
import requests
import globals
from broadcast import broadcast
from vector_clocks import *


internal = Blueprint("internal", __name__, url_prefix="/kvs/internal")

def in_view():
  body = request.get_json()
  ip = body.get('ip')
  if ip not in globals.current_view:
    return False
  return True

@internal.route('/replicate/<key>', methods = ['GET', 'PUT', 'DELETE'])
def propogate_writes(key):

    body = request.get_json()
    other_clock = body.get('vector_clock')
    val = body.get('val')
    other_id = body.get('id')
    source = body.get('source')


    if source not in globals.current_view:
        return "",403 # node was not in the view!
    
    if request.method == 'GET':
        if key not in globals.local_data.keys() and globals.local_data[key] is not None:
            return "",404
        return jsonify(val=globals.local_data[key], vector_clock=globals.local_clocks[key]), 200


    comparison = compare(globals.local_clocks, key, other_clock)

    if comparison == 2 or comparison == -1: 
        # we can actually do the fucking operation!
        if request.method == 'PUT':
            if comparison == -1:
                copy_key(globals.local_clocks, key, other_clock) # copy the new key into ours!
            
            # TODO increment data_clock at the ID of the sender
            if key not in globals.local_data.keys():
                returnVal = 201
            else:
                returnVal = 200
            globals.data[key] = val # set the actual value
            globals.last_write[key] = other_id
            return returnVal

        if request.method == 'DELETE':
            if comparison == -1:
               copy_key(globals.local_clocks, key, other_clock) # copy the new key into ours!

            # TODO increment data_clock at the ID of the sender
            if key in globals.local_data.keys():
                globals.local_data[key] = None
                globals.last_write[key] = other_id
                return 200
            globals.last_write[key] = other_id # ask Ronan about this!
            return 404

    if comparison == 0 or comparison == 1:
        if comparison == 1:
            return
    
        return