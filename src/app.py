from flask import Flask, request, jsonify
from admin import admin
from internal import internal
from data_key import client_side
import os
import globals


app = Flask(__name__)

try:
  globals.address = os.environ['ADDRESS']
except:
  print("we didn't get an address!")

app.register_blueprint(admin, url_prefix="/kvs/admin")
app.register_blueprint(internal, url_prefix="/kvs/internal")
app.register_blueprint(client_side, url_prefix="/kvs/data")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

