from flask import Flask, request, jsonify
import requests
from globals import current_view, data


@app.route('kvs/admin/view', methods = ['GET', 'PUT', 'DELETE'])
def handle_views():

    if request.method == 'GET':
        return jsonify(view=current_view), 200


    elif request.method == 'DELETE':
        current_view.clear()
        data.clear()
        return 200;


    elif request.method == 'PUT': # here comes all the complexity :)
        body = request.get_json()
        new_view = body.get('view') # this is the new view!
        deleted_nodes = [x for x in current_view if x not in new_view] # nodes to delete
        for node in deleted_nodes:
            # address, port = node.split(':')
            url = f"http://{node}/kvs/admin/view"
            requests.delete(url)
        # Nodes that were to be deleted are now deleted!
        for node in new_view: # send the new view and state to all nodes!
            url = f"http://{node}/kvs/admin/update"
            state = {"view":new_view, "data":data}
            requests.put(url, json=state)
    
    else: # unsupported method!
        return 405

    return 200



@app.route('kvs/admin/update', methods = ['PUT'])
def handle_update(): # function and end point for updating nodes with a view update
    body = request.get_json()
    current_view = body.get('view')
    data = body.get('data')
    return 200
