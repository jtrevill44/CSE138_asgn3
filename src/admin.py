from flask import Flask, request, jsonify, Blueprint
import requests
import globals


def find_index() -> int:
    for x in range(len(globals.current_view)):
        if globals.current_view[x] == globals.address:
            return x
    return -1 


admin = Blueprint("admin", __name__, url_prefix="/kvs/admin")

@admin.route('/view', methods = ['GET', 'PUT', 'DELETE'])
def handle_views():

    if (len(request.url) > 2048):
     return jsonify(error='URL is too large'), 414

    if (globals.node_id == -1) and request.method == 'DELETE':
      return jsonify({'error' : 'uninitialized'}), 418

    if request.method == 'GET':
        body = request.get_json()

        if len(body.keys()) >= 1 and 'causal-metadata' not in body.keys():
            return jsonify({"error" : "bad request"}), 400

        return jsonify(view=globals.current_view), 200


    elif request.method == 'DELETE':
        globals.current_view.clear()
        globals.local_data.clear()
        globals.known_clocks.clear()
        globals.last_write.clear()
        globals.node_id = -1
        return "", 200


    elif request.method == 'PUT': # here comes all the complexity :)
        body = request.get_json()

        if 'view' not in body.keys() or len(body.keys()) > 1:
            return jsonify({"error" : "bad request"}), 400

        new_view = body.get('view') # this is the new view!
        deleted_nodes = [x for x in globals.current_view if x not in new_view] # nodes to delete
        for node in deleted_nodes:
            url = f"http://{node}/kvs/admin/view"
            try:
                requests.delete(url, timeout=1)
            except: # could be a partition or something, its fine!
                continue
        # Nodes that were to be deleted are now deleted!

        if len(globals.current_view) < len(new_view):
            for key in globals.local_clocks.keys():
                globals.local_clocks[key].extend([0] * (len(new_view) - len(globals.current_view)))
            for key in globals.known_clocks.keys():
                globals.known_clocks[key].extend([0] * (len(new_view) - len(globals.current_view)))


        globals.current_view = new_view
        globals.node_id = globals.current_view.index(globals.address) # get our new ID

        
        for node in new_view: # send the new view and state to all nodes!
            if node == globals.address:
                continue
            url = f"http://{node}/kvs/admin/update"
            state = {"view":new_view, "kvs":globals.local_data, "vector_clock":globals.local_clocks, "known_clock" : globals.known_clocks}
            try:
                requests.put(url, json=state, timeout=1)
            except: 
                continue
        # globals.syncThread.start()
    else: # unsupported method!
        return "", 405

    return "", 200



@admin.route('/update', methods = ['PUT'])
def handle_update(): # function and end point for updating nodes with a view update
    body = request.get_json()
    globals.current_view = body.get('view')
    globals.local_data = body.get('kvs')
    globals.local_clocks = body.get('vector_clock')
    globals.known_clocks = body.get('known_clock')
    globals.node_id = find_index()
    # globals.syncThread.start()
    return "", 200
