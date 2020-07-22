import pymongo
import redis
import requests
from bson.json_util import dumps
from requests.auth import HTTPBasicAuth


def dump_contents(data, outputfile):
    with open(outputfile, 'w') as outfile:
        outfile.write(dumps(data))


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
            result[database] = []
            r = requests.get(url + '/' + database + '/_all_docs')
            data = r.json()
            try:
                data["rows"]
            except KeyError:
                print("Database requires authentication")
                return
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
            try:
                hits = r.json()["hits"]["hits"]
            except KeyError:
                print("Database requires authentication")
                return
            result[database] = hits

    return result


def extract_mongodb(ip, port, credentials=None):
    result = {}

    if credentials is not None:
        url = "mongodb://%s:%s@%s:%s" % (credentials[0], credentials[1], ip, port)
    else:
        url = "mongodb://%s:%s" % (ip, port)

    myclient = pymongo.MongoClient(url)
    try:
        databases = myclient.list_database_names()
    except pymongo.errors.OperationFailure:
        print("database requires authentication")
        return
    for database in databases:
        if database not in ["admin", "config", "local"]:
            result[database] = {}
            db = myclient[database]
            collections = db.list_collection_names()
            for collection in collections:
                result[database][collection] = []
                col = db[collection]
                for x in col.find():
                    result[database][collection].append(x)
    return result


def extract_redis(ip, port, password=None):
    result = {}
    if password is not None:
        r = redis.StrictRedis(ip, int(port), password=password[0])
    else:
        r = redis.Redis(ip, int(port))
    try:
        keyspace = r.info("keyspace")
    except redis.exceptions.AuthenticationError:
        print("database requires authentication")
        return
    for space in keyspace:
        result[space] = {}

        if password is not None:
            r1 = redis.StrictRedis(ip, int(port), int(space[-1]), password=password[0])
        else:
            r1 = redis.Redis(ip, int(port), int(space[-1]))

        keys = r1.keys("*")
        for key in keys:
            realm = r1.type(key)

            if realm == b"string":
                result[space][key.decode()] = r1.get(key).decode()

            elif realm == b"hash":
                binhash = r1.hgetall(key)
                nonbinhash = {}
                for key1 in binhash:
                    nonbinhash[key1.decode()] = binhash[key1].decode()
                result[space][key.decode()] = nonbinhash

            elif realm == b"list":
                binlist = r1.lrange(key, 0, -1)
                nonbinlist = []
                for value in binlist:
                    nonbinlist.append(value.decode())
                result[space][key.decode()] = nonbinlist

            elif realm == b"set":
                binset = r1.smembers(key)
                nonbinset = set()
                for value in binset:
                    nonbinset.add(value.decode())
                result[space][key.decode()] = nonbinset

            elif realm == b"zset":
                binzset = r1.zrange(key, 0, -1)
                nonbinzset = []
                for value in binzset:
                    nonbinzset.append(value.decode())
                result[space][key.decode()] = nonbinzset

    return result


mapping = {"redis": extract_redis, "mongoDB": extract_mongodb, "elastic": extract_elastic, "couchDB": extract_couchdb}

index = 0


def pretty_print(dictionary, length):
    global index
    if type(dictionary) == dict:
        for value in dictionary:
            if type(dictionary[value]) == str or type(dictionary[value]) == int or type(dictionary[value]) == bool:
                print(str(value) + ": " + str(dictionary[value]))
                index += 1
            elif type(dictionary[value]) == dict or type(dictionary[value]) == list:
                pretty_print(dictionary[value],length)

            if index >= length:
                return
    elif type(dictionary) == list:
        for value in dictionary:
            if type(value) == dict or type(value) == list:
                pretty_print(value,length)




def extract_database(database, ip, port, credentials=None):
    dictionary = mapping[database](ip, port, credentials)
    pretty_print(dictionary,30)
    return dictionary


res = extract_database("redis", "127.0.0.1", "6379", ["admin"])
# res2 = extract_database("mongoDB", "127.0.0.1", "27017", ["admin", "admin"])
# res3 = extract_database("elastic", "127.0.0.1", "9200", ["elastic", "elastic"])
res4 = extract_database("couchDB", "127.0.0.1", "5984", ["admin", "admin"])
'''
dump_contents(res2, "mongoDB.out")
dump_contents(res, "redis.out")
dump_contents(res3, "elastic.out")
dump_contents(res4, "couchDB.out")
'''
