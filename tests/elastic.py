import requests
from requests.auth import HTTPBasicAuth

r = requests.get('http://127.0.0.1:9200/logs/_search', auth=HTTPBasicAuth('elastic','elastic1'))
data = r.text
print(data)
r = requests.get('http://127.0.0.1:9200/_cat/indices?v&pretty')
data = r.text
print(data)
