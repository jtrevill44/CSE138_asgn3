from globals import current_view, data, data_clocks, address
import requests

async def async_request(ip, path, method, key, vector_clock):
  url = f"http://{ip}{path}{method}/{key}"
  state = {"causal-metadata" : vector_clock}
  try:
    if method == 'put':
      return requests.put(url, json=state, timeout=(2/len(current_view)))
    elif method == 'get':
      return requests.get(url, json=state, timeout=(2/len(current_view)))
    else:
      return requests.delete(url, json=state, timeout=(2/len(current_view)))
  except:
    return "Timeout", 404

# Input:
#   method: the method on the end point in string form
#   path: the path of the end point without the key (ie /internal/write/)
#   key: the key in the kvs to modify/get
#   vector_clock: the vector_clock of the node
async def broadcast(method, path, key, vector_clock):
  responses = []
  for node in current_view:
    await responses.append(async_request(node, path, method, key, vector_clock))
  return responses