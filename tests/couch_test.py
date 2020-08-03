import requests


def couchDB_access_test(aggressive, ip, port):
    url = 'http://' + ip + ':' + port + '/_all_dbs'
    r = requests.get(url)
    res = r.json()
    if 'error' in res:
        if aggressive:
            url = 'http://admin:admin@' + ip + ':' + port + '/_all_dbs'
            r = requests.get(url)
            res = r.json()
            if 'error' in res:
                return False, None
            else:
                return True, ('admin','admin')
        else:
            return False, None
    else:
        return True, None

print(couchDB_access_test(True,"127.0.0.1","5984"))