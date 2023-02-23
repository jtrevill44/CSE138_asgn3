from flask import Flask, request, jsonify
from admin import handle_update, handle_views
import os

from globals import address

app = Flask(__name__)

app.config['current_view'] = []
app.config['data'] = {}

try:
  address = os.environ['ADDRESS']
except:
  i = 1




