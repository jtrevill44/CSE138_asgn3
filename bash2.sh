curl -X PUT -d '{"view":["10.10.0.2:8080", "10.10.0.3:8080"]}' -H 'Content-Type: application/json' http://localhost:8081/kvs/admin/view -w '%{http_code}\n'

curl -X PUT -d '{"val": "sampleVal", "causal-metadata": {}}' -H 'Content-Type: application/json' http://localhost:8080/kvs/data/x -w '%{http_code}\n'

curl -X PUT -d '{"val": "FUA", "causal-metadata": {"x": [1,0]}}' -H 'Content-Type: application/json' http://localhost:8081/kvs/data/y -w '%{http_code}\n'

curl -X GET -d '{}' -H 'Content-Type: application/json' http://localhost:8081/kvs/data/y -w '%{http_code}\n'

curl -X GET -d '{"causal-metadata":{"x":[1,0],"y":[0,1]}}' -H 'Content-Type: application/json' http://localhost:8081/kvs/data/x -w '%{http_code}\n'