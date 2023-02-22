from flask import Flask, request, jsonify

data = dict() # kvs!  you guys may wanna move this somewhere else!
current_view = list() # will hold strings in format of "address1:port1" etc.

