from flask import Flask, request, jsonify, Blueprint
import requests
import globals
from broadcast import broadcast
from vector_clocks import *
import pdb


internal = Blueprint("internal", __name__, url_prefix="/kvs/internal")

def in_view():
  body = request.get_json()
  ip = body.get('source')
  if ip not in globals.current_view:
    return False
  return True

@internal.route('/replicate/<key>', methods = ['GET', 'PUT', 'DELETE'])
def propogate_writes(key):

    body = request.get_json()
    other_clock = dict(body.get('vector_clock'))
    val = body.get('val')
    other_id = body.get('id')
    source = body.get('source')
    if source not in globals.current_view:
        return "",403 # node was not in the view!
    
    if request.method == 'GET':
        if key not in globals.local_data.keys():
            return "",404
        return jsonify(val=globals.local_data[key], vector_clock=globals.local_clocks[key], last_write=globals.last_write), 200


    comparison = compare(globals.local_clocks, key, other_clock[key])
    
    if comparison == 2 or comparison == -1: 
        # we can actually do the fucking operation!
        if request.method == 'PUT':
            if comparison == -1:
                copy_key(globals.local_clocks, key, other_clock[key]) # copy the new key into ours!
            
            if key not in globals.local_data.keys():
                returnVal = 201
            else:
                returnVal = 200
            globals.local_data[key] = val # set the actual value
            globals.last_write[key] = other_id
            return "", returnVal

        if request.method == 'DELETE':
            if comparison == -1:
               copy_key(globals.local_clocks, key, other_clock[key]) # copy the new key into ours!

            if key in globals.local_data.keys():
                globals.local_data[key] = None
                globals.last_write[key] = other_id
                return "", 200
            globals.last_write[key] = other_id # ask Ronan about this!
            return "", 404

    if comparison == 0 or comparison == 1:
        if comparison == 1: # we're in the future
            return jsonify(vector_clock=globals.local_clocks[key],val=val), 200
        
        if comparison == 0: # we're concurrent
            # do tie break:
            if request.method == 'PUT':
                if globals.last_write[key] < other_id: # the vaue we have right now wins!
                    return"", 200
                else: # we're gonna do the put
                    if key not in globals.local_data.keys():
                        returnVal = 201
                    else:
                        returnVal = 200
                    globals.data[key] = val # set the actual value
                    globals.local_clocks[key] = other_clock[key]
                    globals.last_write[key] = other_id
                    return "", returnVal
            else: # it is a delete!
                if globals.last_write[key] < other_id:
                    return "", 200
                else:
                     if key in globals.local_data.keys():
                        globals.local_data[key] = None
                        globals.local_clocks[key] = other_clock[key]
                        globals.last_write[key] = other_id
                        return "", 200
                     else:
                        globals.last_write[key] = other_id # ask Ronan about this!
                        return "", 404


@internal.route('/kvs', methods=['GET'])
def get_all():
    body = request.get_json()
    other_id = body.get('id')
    source = body.get('source')
    other_clock = dict(body.get('vector_clock'))
    return jsonify(vector_clock= globals.local_clocks, kvs= globals.local_data, last_write= globals.last_write), 200

@internal.route('/sync', methods=['PUT'])
def sync_kvs_local_clocks():
    json = request.get_json()
    got_clocks = dict(json.get('vector_clock'))
    got_data = dict(json.get('key'))
    got_last_write = dict(json.get('id'))
    all_keys = set().union(globals.local_data.keys(), got_data.keys())
    for key in all_keys:
        if compare(globals.local_clocks, key, got_clocks[key]) == -1:
            globals.local_data[key] = got_data[key]
            globals.local_clocks[key] = got_clocks[key]
            globals.last_write[key] = got_last_write[key]
        elif compare(globals.local_clocks, key, got_clocks[key]) == 0 and globals.current_view.index(globals.last_write[key]) > globals.current_view.index(got_last_write[key]):
            globals.local_data[key] = got_data[key]
            combine(globals.local_clocks, key, got_clocks[key])
            globals.last_write[key] = got_last_write[key]
        # maybe sanity check if the vector clocks are the same?
    return jsonify(success='updated clocks from sync'), 200
