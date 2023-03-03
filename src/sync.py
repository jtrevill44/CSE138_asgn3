import globals
from flask import Flask, request, jsonify, Blueprint
import requests
import schedule
import time



def send_request():
    url = f'http://{globals.address}/kvs/data'
    response = requests.get(url)

def sync():
    schedule.every(5).seconds.do(send_request)
    while True:
        schedule.run_pending()
        time.sleep(1)
        