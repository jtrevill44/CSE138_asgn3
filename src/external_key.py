from flask import Blueprint, request
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

    for i in responses:
        if i != -1 and i.status_code != 500:
            return i

    return "timeouterror msg" 
