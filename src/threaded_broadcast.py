from threading import Thread
import requests

import globals

def make_request(ip, path, method, key = None, vector_clock = dict(), val = None,  node_id = globals.node_id, source = globals.address):
	url = f"http://{ip}{path}"
	state = {"key": key, "val": val, "vector_clock" : vector_clock, "id" : node_id, "source" : source}
	try:
		if method == 'PUT':
			return requests.put(url, json=state, timeout=(2))
		elif method == 'GET':
			return requests.get(url, json=state, timeout=(2))
		else:
			return requests.delete(url, json=state, timeout=(2))
	except:
		return -1

class BroadcastThread(Thread):
    def __init__(self, group=None, target=None, name = None, args=(), kwargs=()):
        Thread.__init__(self, group, target, name, args, kwargs)

    def run(self):
        if self.target != None: 
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def broadcast_await(method, path, key, vector_clock, val=None, node_id = globals.node_id, source = globals.address):
    threads = []
    responses = []
    for node in globals.current_view:
        threads.append(BroadcastThread(target=make_request, kwargs={"ip" : node, "path" : path, "method" : method, "key" : key, "vector_clock" : vector_clock, "val" : val, "node_id": node_id, "source" : source}))
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        responses.append(thread.join())

    return responses

def broadcast_async(method, path, key, vector_clock, val=None, node_id = globals.node_id, source = globals.address):
    threads = []
    responses = []
    for node in globals.current_view:
        threads.append(BroadcastThread(target=make_request, kwargs={"ip" : node, "path" : path, "method" : method, "key" : key, "vector_clock" : vector_clock, "val" : val, "node_id": node_id, "source" : source}))
    
    for thread in threads:
        thread.start()
