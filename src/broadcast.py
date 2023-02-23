from globals import current_view, data, data_clocks, address
import asyncio
import requests

async def async_request(ip, path, method, key, vector_clock):
  url = f"http://{ip}{path}{method}/{key}"
  state = {"causal-metadata" : vector_clock, "source" : address}
  try:
    if method == 'PUT':
      return requests.put(url, json=state, timeout=(2/len(current_view)))
    elif method == 'GET':
      return requests.get(url, json=state, timeout=(2/len(current_view)))
    else:
      return requests.delete(url, json=state, timeout=(2/len(current_view)))
  except:
    return -1

# Input:
#   method: the method on the end point in string form
#   path: the path of the end point without the key (ie /internal/write/)
#   key: the key in the kvs to modify/get
#   vector_clock: the vector_clock of the node
async def broadcast(method, path, key, vector_clock):
  tasks = []
  for node in current_view:
    task = asyncio.create_task(async_request(node, path, method, key, vector_clock))
    tasks.append(task)
  responses = await asyncio.gather(*tasks)
  return responses