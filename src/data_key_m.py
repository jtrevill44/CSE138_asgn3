from flask import Flask, request, jsonify, Blueprint
import requests
from globals import current_view, data, data_clocks, address

blueprint = Blueprint('blueprint', __name__)

@blueprint.route('kvs/data/<key>', methods = ['PUT'])
def handle_put(key):
  return 200


@blueprint.route('kvs/data/rep/<key>', methods = ['PUT',])
def handle_rep_put(key):
  return 200
