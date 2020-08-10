import pymongo
import redis
import requests
from bson.json_util import dumps
from requests.auth import HTTPBasicAuth
import rethinkdb
import cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


class DatabaseAuthenticationError(Exception):
    def __init__(self, message):
        self.message = message


class DatabaseConnectionError(Exception):
    def __init__(self, message):
        self.message = message


def dump_contents(data, outputfile):
    with open(outputfile, 'w') as outfile:
        outfile.write(dumps(data))


def extract_couchdb(ip, port, credentials=None):
    result = {}
    if credentials is not None:
        url = 'http://%s:%s@%s:%s' % (credentials[0], credentials[1], ip, port)
    else:
        url = 'http://%s:%s' % (ip, port)
    try:
        r = requests.get(url + '/_all_dbs')
    except requests.exceptions.ConnectionError:
        raise DatabaseConnectionError("No couchDB instance found running at this address")
    data = r.json()
    for database in data:
        if database[0] != '_':
            result[database] = []
            r = requests.get(url + '/' + database + '/_all_docs')
            data = r.json()
            try:
                data["rows"]
            except KeyError:
                raise DatabaseAuthenticationError("Could not authenticate with provided credentials")
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


def extract_cassandra(ip, port, credentials=None):
    result = {}
    if credentials is None:
        cluster = Cluster([ip], port=port)
    else:
        auth = PlainTextAuthProvider(credentials[0], credentials[1])
        cluster = Cluster([ip], port=port, auth_provider=auth)
    try:
        cluster.connect()
    except cassandra.cluster.NoHostAvailable as err:
        print(err)
        if type(err.errors[ip + ":" + port]) == cassandra.AuthenticationFailed:
            raise DatabaseAuthenticationError("Could not authenticate with provided credentials")
        elif type(err.errors[ip+":"+port]) == ConnectionRefusedError:
            raise DatabaseConnectionError("No cassandraDB instance found running at this address")
    for keyspace in cluster.metadata.keyspaces:
        if "system" not in keyspace:
            result[keyspace] = {}
            session = cluster.connect(keyspace=keyspace)
            session.row_factory = cassandra.query.dict_factory
            act_keyspace = cluster.metadata.keyspaces[keyspace]
            for table in act_keyspace.tables:
                result[keyspace][table] = []
                cql = 'Select * from ' + table
                rows = session.execute(cql)
                for row in rows:
                    result[keyspace][table].append(row)
    return result


def extract_elastic(ip, port, credentials=None):
    result = {}

    if credentials is not None:
        authentication = HTTPBasicAuth(credentials[0], credentials[1])
    else:
        authentication = None
    url = 'http://%s:%s' % (ip, port)
    try:
        r = requests.get(url + '/_aliases', auth=authentication)
    except requests.exceptions.ConnectionError:
        raise DatabaseConnectionError("No elasticsearch instance found running at this address")
    data = r.json()
    for database in data:
        if database[0] != '.' and database != "kibana_sample_data_logs":
            r = requests.get(url + '/' + database + '/_search/?size=1000', auth=authentication)
            try:
                hits = r.json()["hits"]["hits"]
            except KeyError:
                raise DatabaseAuthenticationError("Could not authenticate with provided credentials")
            result[database] = hits

    return result


def extract_mongodb(ip, port, credentials=None):
    result = {}

    if credentials is not None:
        url = "mongodb://%s:%s@%s:%s" % (credentials[0], credentials[1], ip, port)
    else:
        url = "mongodb://%s:%s" % (ip, port)

    myclient = pymongo.MongoClient(url,serverSelectionTimeoutMS=5000)
    try:
        databases = myclient.list_database_names()
    except pymongo.errors.OperationFailure:
        raise DatabaseAuthenticationError("Could not authenticate with provided credentials")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise DatabaseConnectionError("No mongoDB instance found running at this address")
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


def extract_rethinkdb(ip, port, credentials=None):
    result = {}
    r = rethinkdb.RethinkDB()
    if credentials is not None:
        try:
            r.connect(ip, int(port), user=credentials[0], password=credentials[1]).repl()
        except rethinkdb.errors.ReqlAuthError:
            raise DatabaseAuthenticationError("Could not authenticate with provided credentials")
        except rethinkdb.errors.ReqlDriverError:
            raise DatabaseConnectionError("No rethinkDB instance found running at this address")
    else:
        try:
            r.connect(ip, int(port)).repl()
        except rethinkdb.errors.ReqlAuthError:
            raise DatabaseAuthenticationError("Could not authenticate with provided credentials")
        except rethinkdb.errors.ReqlDriverError:
            raise DatabaseConnectionError("No rethinkDB instance found running at this address")


    databases = r.db_list().run()
    for database in databases:
        if database != "rethinkdb":
            result[database] = {}
            tables = r.db(database).table_list().run()
            for table in tables:
                result[database][table] = []
                cursor = r.db(database).table(table).run()
                for doc in cursor:
                    result[database][table].append(doc)
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
        raise DatabaseAuthenticationError("Could not authenticate with provided credentials")
    except redis.exceptions.ConnectionError:
        raise DatabaseConnectionError("No redis instance found running at this address")
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


mapping = {"redis": extract_redis, "mongodb": extract_mongodb, "elastic": extract_elastic, "couchdb": extract_couchdb,
           "cassandradb": extract_cassandra, "rethinkdb": extract_rethinkdb}

index = 0


def pretty_print(dictionary, length):
    global index
    if type(dictionary) == dict:
        for value in dictionary:
            if type(dictionary[value]) == str or type(dictionary[value]) == int or type(dictionary[value]) == bool:
                print(str(value) + ": " + str(dictionary[value]))
                index += 1
            elif type(dictionary[value]) == dict or type(dictionary[value]) == list:
                pretty_print(dictionary[value], length)

            if index >= length:
                return
    elif type(dictionary) == list:
        for value in dictionary:
            if type(value) == dict or type(value) == list:
                pretty_print(value, length)


def extract_database(database, ip, port, credentials=None):
    global index
    index = 0
    dictionary = mapping[database](ip, port, credentials)
    pretty_print(dictionary, 30)
    return dictionary


extract_database("cassandradb","127.0.0.1","9042",["cassandra","cassandra"])

'''
res = extract_database("mongodb","127.0.0.1","27017")
dump_contents(res,"mongoDB.json")
res1 = extract_database("cassandradb","127.0.0.1","9042",["cassandra","cassandra"])
dump_contents(res1,"cassandraDB.json")
'''

# res = extract_database("redis", "127.0.0.1", "6379", ["admin"])
# res2 = extract_database("mongoDB", "127.0.0.1", "27017", ["admin", "admin"])
# res3 = extract_database("elastic", "127.0.0.1", "9200", ["elastic", "elastic"])
# res4 = extract_database("couchDB", "127.0.0.1", "5984", ["admin", "admin"])
'''
dump_contents(res2, "mongoDB.out")
dump_contents(res, "redis.out")
dump_contents(res3, "elastic.out")
dump_contents(res4, "couchDB.out")
'''
