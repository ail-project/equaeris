import pymongo
import redis
import json
from bson.json_util import dumps

def dump_contents(data,outputfile):
    with open(outputfile,'w') as outfile:
        outfile.write(dumps(data))


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


mapping = {"redis": extract_redis, "mongodb": extract_mongodb}


def extract_database(database, ip, port, credentials=None):
    return mapping[database](ip, port, credentials)


res2 = extract_database("redis", "127.0.0.1", "6379", ["admin"])
res = extract_database("mongodb", "127.0.0.1", "27017", ["admin", "admin"])
dump_contents(res,"mongoDB.out")
dump_contents(res2,"redis.out")