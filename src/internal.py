from flask import Flask, request, jsonify, Blueprint
import requests
from globals import current_view, data, data_clocks, address
from broadcast import broadcast
from vector_clocks import Vector_Clock

@app.route('kvs/internal/broadcast', methods = ['PUT', 'DELETE'])
def propogate_writes():

     body = request.get_json()
     other_clock = body.get('vector_clock')
     key = body.get('key')
     val = body.get('val')

     comparison = data_clocks.compare(other_clock, key)

     if comparison == 2 or comparison == -1: 
        # we can actually do the fucking operation!
        if request.method == 'PUT':
            if comparison == -1:
                data_clocks.copy_key(key, other_clock) # copy the new key into ours!
            
            # TODO increment data_clock at the ID of the sender
            if key not in data.keys():
                returnVal = 201
            else:
                returnVal = 200
            data[key] = val # set the actual value
            return returnVal

        if request.method == 'DELETE':
            if comparison == -1:
                data_clocks.copy_key(key, other_clock) # copy the new key into ours!

            # TODO increment data_clock at the ID of the sender
            if key in data.keys():
                del data[key]
                return 200
            return 404

     if comparison == 0 or comparison == 1:
        # TODO
        # we have to do some searching here!
        # talk about this section in the meeting tomorrow
    
        return