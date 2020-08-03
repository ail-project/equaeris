import requests
from requests.auth import HTTPBasicAuth

def elastic_access_test(aggressive, ip, port):
    url = 'http://' + ip + ':' + port + '/_aliases'
    r = requests.get(url)
    res = r.json()
    if 'error' in res:
        if aggressive:
            r = requests.get(url, auth=HTTPBasicAuth('elastic','elastic'))
            res = r.json()
            if 'error' in res:
                return False, None
            else:
                return True, ("elastic","elastic")
        else:
            return False, None
    else:
        return True, None

print(elastic_access_test(True, '127.0.0.1', '9200'))