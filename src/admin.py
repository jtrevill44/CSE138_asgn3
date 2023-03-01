from flask import Flask, request, jsonify, Blueprint
import requests
import globals


admin = Blueprint("admin", __name__, url_prefix="/kvs/admin")

@admin.route('/view', methods = ['GET', 'PUT', 'DELETE'])
def handle_views():

    if request.method == 'GET':
        return jsonify(view=globals.current_view), 200


    elif request.method == 'DELETE':
        globals.current_view.clear()
        globals.local_data.clear()
        return "", 200


    elif request.method == 'PUT': # here comes all the complexity :)
        body = request.get_json()
        new_view = body.get('view') # this is the new view!
        deleted_nodes = [x for x in globals.current_view if x not in new_view] # nodes to delete
        for node in deleted_nodes:
            url = f"http://{node}/kvs/admin/view"
            requests.delete(url)
        # Nodes that were to be deleted are now deleted!
        globals.current_view = new_view
        for node in new_view: # send the new view and state to all nodes!
            if node == globals.address:
                continue
            url = f"http://{node}/kvs/admin/update"
            state = {"view":new_view, "data":globals.local_data}
            requests.put(url, json=state, timeout=2)
    
    else: # unsupported method!
        return "", 405

    return "", 200



@admin.route('/update', methods = ['PUT'])
def handle_update(): # function and end point for updating nodes with a view update
    body = request.get_json()
    globals.current_view = body.get('view')
    globals.local_data = body.get('data')
    return 200
