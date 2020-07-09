import requests
url = 'http://admin:test@127.0.0.1:5984'
r = requests.get(url + '/_all_dbs')
data = r.json()
for database in data:
    if database[0] != '_':
        print(database)
        r = requests.get(url+'/'+database+'/_all_docs')
        data = r.json()
        for doc in data["rows"]:
            id = doc["id"]
            r = requests.get(url + '/' + database + '/' + id)
            data = r.json()
            print(data)
            if "_attachments" in data:
                attachments = data["_attachments"]
                for files in attachments:
                    r = requests.get(url + '/' + database + '/' + id + '/' + files)
                    print(files + ':')
                    print(r.text)