from flask import Flask, request, jsonify
from admin import admin
import os

import globals

def find_index() -> int:
    for x in range(len(globals.current_view)):
        if globals.current_view[x] == globals.address:
            return x
    return -1 



app = Flask(__name__)
app.register_blueprint(admin, url_prefix="/kvs/admin")


try:
  globals.address = os.environ['ADDRESS']
  globals.node_id = find_index()
except:
  print("we didn't get an address!")




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

