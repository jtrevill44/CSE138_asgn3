from flask import Blueprint, request, jsonify
import hashlib
import asyncio
from broadcast import broadcast_shard, broadcast_request
import globals
from vector_clocks import update_known_clocks

external_key = Blueprint('external_key', __name__, url_prefix='/kvs/data')

@external_key.route('/<key>', methods = ['GET', 'PUT', 'DELETE'])
def external_route(key):

    n = int(hashlib.sha256(key.encode()).hexdigest(),16) % len(globals.shard_view)
    responses = asyncio.run(broadcast_request(globals.shard_view.get(n, []), request, f"/internal/{key}"))

    if request.method == "DELETE":
        for i in responses: 
            if i.status_code == 200:
                globals.known_clocks
                body = i.get_json()
                causal_metadata = body.get('causal-metadata', None)
                update_known_clocks(causal_metadata)
                return i
        for i in responses:
            if i != -1:
                body = i.get_json()
                causal_metadata = body.get('causal-metadata', None)
                update_known_clocks(causal_metadata)
                return i
            
    for i in responses:
        if i != -1 and i.status_code != 500:
            body = i.get_json()
            causal_metadata = body.get('causal-metadata', None)
            update_known_clocks(causal_metadata)
            return i

    return jsonify({"causal-metadata" : globals.known_clocks, "error" : "timed out while waiting for depended updates"}), 500
