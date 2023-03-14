from flask import Flask, request, jsonify, Blueprint
from admin import admin
from internal import internal
from data_key import client_side
from kvs import get_all
from sync import sync_2
import os
import globals
from flask_apscheduler import APScheduler

def is_valid_ipv4_address(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or int(part) > 255 or int(part) < 0:
            return False
    return True



kvs_app = Blueprint("kvs_app",__name__, url_prefix="/internal_shard" )
scheduler = APScheduler()
track_var = 0

try:
  globals.address = os.environ['ADDRESS']
  if is_valid_ipv4_address(globals.address.split(":")[0]) == False:
    track_var = 1
  if not globals.address.split(":")[1]:
    track_var = 1
except:
  track_var = 1


kvs_app.register_blueprint(admin, url_prefix="/kvs/admin")
kvs_app.register_blueprint(internal, url_prefix="/kvs/internal")
kvs_app.register_blueprint(client_side, url_prefix="/kvs/data")
kvs_app.register_blueprint(get_all)
scheduler.add_job(id = 'Scheduled Task', func=sync_2, trigger="interval", seconds=3)

if __name__ == "__main__":
    if track_var == 1:
      exit(1)
    scheduler.start()
