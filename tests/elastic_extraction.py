import requests
from requests.auth import HTTPBasicAuth


def extract_elastic(ip, port, credentials=None):
    result = {}

    if credentials is not None:
        authentication = HTTPBasicAuth(credentials[0], credentials[1])
    else:
        authentication = None
    url = 'http://%s:%s' % (ip, port)
    r = requests.get(url + '/_aliases', auth=authentication)
    data = r.json()
    for database in data:
        if database[0] != '.' and database != "kibana_sample_data_logs":
            r = requests.get(url + '/' + database + '/_search/?size=1000', auth=authentication)
            hits = r.json()["hits"]["hits"]
            result[database] = hits

    return result
print(extract_elastic("127.0.0.1", "9200",("elastic","elastic")))
