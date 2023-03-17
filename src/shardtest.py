import string
import sys
import time
import random
import unittest

import requests


def usage():
    print(
        f'Usage: {sys.argv[0]} local_port1:ip1:port1 local_port2:ip2:port2 [local_port3:ip3:port3...]')
    sys.exit(1)


def check_arg_count():
    if len(sys.argv) < 3:
        usage()

def parse_args():
    check_arg_count()
    local_ports = []
    view = []
    for arg in sys.argv[1:]:
        try:
            col1_idx = arg.find(':')
            local_ports.append(int(arg[:col1_idx]))
            view.append(arg[col1_idx+1:])
        except:
            usage()
    return local_ports, view

ports, view_addresses = parse_args()
hosts = ['localhost'] * len(ports)
keys = ['key1', 'key2', 'key3']
vals = ['Value 1', 'val2', 'third_value']
causal_metadata_key = 'causal-metadata'

# Requests:


def get(url, body={}):
    return requests.get(url, json=body)


def put(url, body={}):
    return requests.put(url, json=body)


def delete(url, body={}):
    return requests.delete(url, json=body)


# URLs:


def make_base_url(port, host='localhost', protocol='http'):
    return f'{protocol}://{host}:{port}'


def kvs_view_admin_url(port, host='localhost'):
    return f'{make_base_url(port, host)}/kvs/admin/view'


def kvs_data_key_url(key, port, host='localhost'):
    return f'{make_base_url(port, host)}/kvs/data/{key}'


def kvs_data_url(port, host='localhost'):
    return f'{make_base_url(port, host)}/kvs/data'

# Bodies:


def nodes_list(ports, hosts=None):
    if hosts is None:
        hosts = ['localhost'] * len(ports)
    return [f'{h}:{p}' for h, p in zip(hosts, ports)]


def put_view_body(addresses, total_shards):
    return {'nodes': addresses, 'num_shards':total_shards}


def causal_metadata_body(cm={}):
    return {causal_metadata_key: cm}


def causal_metadata_from_body(body):
    return body[causal_metadata_key]


def put_val_body(val, cm=None):
    body = causal_metadata_body(cm)
    body['val'] = val
    return body

class TestAssignment(unittest.TestCase):
    #delete every node
    def setUp(self):
        for h, p in zip(hosts,ports):
            delete(kvs_view_admin_url(p,h))

    def test_distribution(self):
        #initialize the view, with ~half as many shards as nodes
        res = put(kvs_view_admin_url(ports[0], hosts[0]),
                  put_view_body(view_addresses, len(hosts)//2))
        self.assertEqual(res.status_code, 200, msg="Bad status code on PUT view")

        time.sleep(1)

        for _ in range(1000):
            #generate random key and value pair
            k = ''.join(random.choice(string.ascii_letters) for _ in range(10))
            v = ''.join(random.choice(string.ascii_letters) for _ in range(10))
            rand_node = random.choice(range(len(hosts)))
            put(kvs_data_key_url(k, ports[rand_node], hosts[rand_node]), 
                put_val_body(v))

        #check keys are appro
        for h, p in zip(hosts, ports):
            res = get(kvs_data_url(p, h))
            print(res.json().get('count')/2, 100/2)
            self.assertAlmostEqual(res.json().get('count'), 1000/2)

        #send a viewchange with a different number of nodes
        res = put(kvs_view_admin_url(ports[0], hosts[0]),
                  put_view_body(view_addresses, len(ports)//3))
            
        for h, p in zip(hosts, ports):
            res = get(kvs_data_url(p, h))
            print(res.json().get('count')/3, 100/3)
            self.assertAlmostEqual(res.json().get('count'), 1000/3)


if __name__ == '__main__':
    unittest.main(argv=["first-arg-ignored"], exit=False)
