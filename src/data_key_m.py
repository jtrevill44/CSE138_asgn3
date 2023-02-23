from flask import Flask, request, jsonify, Blueprint
import requests
from globals import current_view, data, data_clocks, address
from broadcast import broadcast

blueprint = Blueprint('blueprint', __name__)

def quorum_rep():
  return 'hi'

@blueprint.route('kvs/data/<key>', methods = ['PUT'])
def handle_put(key):
  return 200


@blueprint.route('/internal/write/<key>', methods = ['PUT', 'DELETE'])
def handle_rep_put(key):
  return 200
