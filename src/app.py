from flask import Flask, request, jsonify
from admin import handle_update, handle_views

app = Flask(__name__)

app.config['current_view'] = []
app.config['data'] = {}




