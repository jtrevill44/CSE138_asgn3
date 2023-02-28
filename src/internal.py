from flask import Flask, request, jsonify, Blueprint
import requests
import globals
from broadcast import broadcast
from vector_clocks import Vector_Clock


@app.route('kvs/internal/broadcast', methods = ['PUT', 'DELETE'])
def propogate_writes():

    body = request.get_json()
    other_clock = body.get('vector_clock')
    key = body.get('key')
    val = body.get('val')

    source_ip = request.remote_addr
    source_port = "8080" # TODO might have to change this idk
    source = f"{source_ip}:{source_port}" # we need to check if this address is in current_view

    if source not in globals.current_view:
        return 403 # node was not in the view!
    

    comparison = globals.data_clocks.compare(other_clock, key)

    if comparison == 2 or comparison == -1: 
        # we can actually do the fucking operation!
        if request.method == 'PUT':
            if comparison == -1:
                globals.data_clocks.copy_key(key, other_clock) # copy the new key into ours!
            
            # TODO increment data_clock at the ID of the sender
            if key not in globals.data.keys():
                returnVal = 201
            else:
                returnVal = 200
            globals.data[key] = val # set the actual value
            return returnVal

        if request.method == 'DELETE':
            if comparison == -1:
                globals.data_clocks.copy_key(key, other_clock) # copy the new key into ours!

            # TODO increment data_clock at the ID of the sender
            if key in globals.data.keys():
                del globals.data[key]
                return 200
            return 404

    if comparison == 0 or comparison == 1:
        # TODO
        # we have to do some searching here!
        # talk about this section in the meeting tomorrow
    
        return