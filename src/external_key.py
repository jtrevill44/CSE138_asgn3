from flask import Blueprint, request
import hashlib
import asyncio

from broadcast import broadcast_shard
import globals

external_key = Blueprint('external_key', __name__, url_prefix='/kvs/data')

@external_key.route('/<key>')
def external_route(key):
    n = int(hashlib.sha256(key).hexdigest(),16) % len(globals.shard_view)
    responses = broadcast_request(shard_view.get(n, []), request, f"/internal/kvs/data/{key}")

    if request.method == 'DELETE':
        for i in responses:
            if i.code == 200:
                return i
        return responses[0]

    for i in responses:
        if i != -1:
            return i

    return "timeouterror msg" 
