import requests


url = 'http://127.0.0.1:9200'
r = requests.get(url + '/_aliases')
data = r.json()
for database in data:
    if database[0] != '.':
        print(database)
        r = requests.get(url + '/' + database + '/_search/?size=1000')
        hits = r.json()["hits"]["hits"]
        print(hits)
        print()
