import requests


def extract_couchdb(ip, port, credentials=None):
    result = {}

    if credentials is not None:
        url = 'http://%s:%s@%s:%s' % (credentials[0], credentials[1], ip, port)
    else:
        url = 'http://%s:%s' % (ip, port)
    r = requests.get(url + '/_all_dbs')
    data = r.json()
    for database in data:
        if database[0] != '_':
            print(database)
            result[database] = []
            r = requests.get(url + '/' + database + '/_all_docs')
            data = r.json()
            for doc in data["rows"]:
                iden = doc["id"]
                r = requests.get(url + '/' + database + '/' + iden)
                data = r.json()
                result[database].append(data)
                if "_attachments" in data:
                    attachments = data["_attachments"]
                    for file in attachments:
                        r = requests.get(url + '/' + database + '/' + iden + '/' + file)
                        outputfile = file
                        open(outputfile, "wb").write(r.content)

    return result


print(extract_couchdb("127.0.0.1", "5984"))
