import requests
from requests.auth import HTTPBasicAuth



def extract_elastic(ip,port,credentials = None):
    if credentials is not None:
        authentication = HTTPBasicAuth('elastic','elastic')
    else:
        authentication = None
    url = 'http://%s:%s' % (ip,port)
    r = requests.get(url + '/_aliases', auth=authentication)
    data = r.json()
    for database in data:
        if database[0] != '.':
            print(database)
            r = requests.get(url + '/' + database + '/_search/?size=1000', auth=authentication)
            hits = r.json()["hits"]["hits"]
            print(hits)
            print()
