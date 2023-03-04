from flask import Flask, request, jsonify
from admin import admin
from internal import internal
from data_key import client_side
from kvs import get_all
from sync import sync_2
import os
import globals
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()

try:
  globals.address = os.environ['ADDRESS']
except:
  globals.address = "127.0.0.1:5000"


app.register_blueprint(admin, url_prefix="/kvs/admin")
app.register_blueprint(internal, url_prefix="/kvs/internal")
app.register_blueprint(client_side, url_prefix="/kvs/data")
app.register_blueprint(get_all)


if __name__ == "__main__":
    scheduler.add_job(id = 'Scheduled Task', func=sync_2, trigger="interval", seconds=3)
    scheduler.start()
    app.run(host='0.0.0.0', port=8080)


