import requests


def extract_couchdb(ip, port, credentials=None):
    if credentials is not None:
        url = 'http://%s:%s@%s:%s' % (credentials[0], credentials[1], ip, port)
    else:
        url = 'http://%s:%s' % (ip, port)
    r = requests.get(url + '/_all_dbs')
    data = r.json()
    for database in data:
        if database[0] != '_':
            print(database)
            r = requests.get(url + '/' + database + '/_all_docs')
            data = r.json()
            for doc in data["rows"]:
                iden = doc["id"]
                r = requests.get(url + '/' + database + '/' + iden)
                data = r.json()
                print(data)
                if "_attachments" in data:
                    attachments = data["_attachments"]
                    for files in attachments:
                        r = requests.get(url + '/' + database + '/' + iden + '/' + files)
                        print(files + ':')
                        print(r.text)
