from flask import Flask, request, jsonify
from admin import handle_update, handle_views
import os

import globals

app = Flask(__name__)



try:
  globals.address = os.environ['ADDRESS']
except:
  i = 1




