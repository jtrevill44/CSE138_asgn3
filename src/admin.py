from flask import Flask, request, jsonify


@app.route('kvs/admin/view', methods = ['GET', 'PUT', 'DELETE'])
def handle_views():

    if request.method == 'GET':
        return jsonify(view=current_view), 200

    elif request.method == 'DELETE':
        current_view.clear()
        data.clear()
        return 200;
    elif request.method == 'PUT': # here comes all the complexity :)
        
