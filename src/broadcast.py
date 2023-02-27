from globals import current_view, data, data_clocks, address
import asyncio
import requests

async def async_request(ip, path, method, key, vector_clock, val=None):
  url = f"http://{ip}{path}{method}/{key}"
  state = {"val": val, "causal-metadata" : vector_clock, "source" : address}
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
async def broadcast(method, path, key, vector_clock, val=None):
  tasks = []
  for node in current_view:
    task = asyncio.create_task(async_request(node, path, method, key, vector_clock, val))
    tasks.append(task)
  responses = await asyncio.gather(*tasks)
  return responses