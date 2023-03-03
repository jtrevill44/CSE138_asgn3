import globals
import asyncio
import requests

async def async_request(ip, path, method, key = None, vector_clock = dict(), val = None, node_id = globals.node_id, source = globals.address):
  url = f"http://{ip}{path}"
  # path needs to include the /<key> if that endpoint needs one
  state = {"key": key, "val": val, "vector_clock" : vector_clock, "id" : node_id, "source" : source}
  # print(state)
  try:
    if method == 'PUT':
      return requests.put(url, json=state, timeout=(2))
    elif method == 'GET':
      return requests.get(url, json=state, timeout=(2))
    else:
      return requests.delete(url, json=state, timeout=(2))
  except:
    return -1

# Input:
#   method: the method on the end point in string form
#   path: the path of the end point without the key (ie /internal/write/)
#   key: the key in the kvs to modify/get
#   vector_clock: the vector_clock of the node
#
# Output:
#   responses: a list of responses given from all the requests
async def broadcast(method, path, key, vector_clock, val=None, node_id = globals.node_id, source = globals.address):
  tasks = []
  for node in globals.current_view:
    task = asyncio.create_task(async_request(ip = node, path = path, method = method, key = key, vector_clock= vector_clock, val = val, node_id= node_id, source = source))
    tasks.append(task)
  responses = await asyncio.gather(*tasks)
  return responses