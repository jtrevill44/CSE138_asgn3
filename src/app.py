import sys

from flask import Flask

sys.path.append('kvs')
from kvs_blueprint import kvs_app, scheduler

app = Flask(__name__)

app.register_blueprint(kvs_app, url_prefix="/internal_shard")

if __name__ == "__main__":
    scheduler.start()
    app.run(host='0.0.0.0', port=8080)
