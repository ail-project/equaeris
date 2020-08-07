import xml.etree.ElementTree as ET
import json
import pymongo
import redis
import requests
from requests.auth import HTTPBasicAuth
import cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import rethinkdb


class DatabaseConnectionError(Exception):
    def __init__(self, message):
        self.message = message


def parse_nmap(nmapfile):
    tree = ET.parse(nmapfile)
    root = tree.getroot()
    ports = root[3][3]
    res = []
    for child in ports:
        try:
            res.append(child.attrib['portid'])
        except KeyError:
            pass
    return res


def database_check(open_ports):
    result = []
    with open('ports.json', 'r') as json_file:
        json_data = json_file.readline()
        db_ports = json.loads(json_data)
        for port in open_ports:
            if port in db_ports:
                result.append((db_ports[port], port))
                # print("Open", db_ports[port], "at port", port)
    return result


def couchdb_access_test(aggressive, ip, port):
    url = 'http://' + ip + ':' + port + '/_all_dbs'
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        raise DatabaseConnectionError("no couchDB instance found running at this address")
    res = r.json()
    if 'error' in res:
        if aggressive:
            url = 'http://admin:admin@' + ip + ':' + port + '/_all_dbs'
            r = requests.get(url)
            res = r.json()
            if 'error' in res:
                return False, None
            else:
                return True, ('admin', 'admin')
        else:
            return False, None
    else:
        return True, None


def elastic_access_test(aggressive, ip, port):
    url = 'http://' + ip + ':' + port + '/_aliases'
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        raise DatabaseConnectionError("no elasticsearch instance found running at this address")
    res = r.json()
    if 'error' in res:
        if aggressive:
            r = requests.get(url, auth=HTTPBasicAuth('elastic', 'elastic'))
            res = r.json()
            if 'error' in res:
                return False, None
            else:
                return True, ("elastic", "elastic")
        else:
            return False, None
    else:
        return True, None


def rethinkdb_access_test(aggressive, ip, port):
    r = rethinkdb.RethinkDB()
    try:
        r.connect(ip, int(port))
        return True, None
    except rethinkdb.errors.ReqlAuthError:
        if aggressive:
            try:
                r.connect(ip, int(port), user="admin", password="admin")
                return True, ("admin", "admin")
            except rethinkdb.errors.ReqlAuthError:
                return False, None
        else:
            return False, None
    except rethinkdb.errors.ReqlDriverError:
        raise DatabaseConnectionError("no rethinkDB instance found running at this address")


def cassandra_access_test(aggressive, ip, port):
    cluster = Cluster([ip], port=port)
    try:
        cluster.connect()
        return True, None
    except cassandra.cluster.NoHostAvailable:
        if not aggressive:
            return False, None
        else:
            auth = PlainTextAuthProvider("cassandra", "cassandra")
            cluster = Cluster([ip], port=int(port), auth_provider=auth)
            try:
                cluster.connect()
                return True, ("cassandra", "cassandra")
            except cassandra.cluster.NoHostAvailable:
                return False, None


def mongodb_access_test(aggressive, ip, port):
    url = "mongodb://%s:%s" % (ip, port)
    myclient = pymongo.MongoClient(url, serverSelectionTimeoutMS=5000)
    try:
        myclient.list_database_names()
        return True, None
    except pymongo.errors.OperationFailure:
        if aggressive:
            credentials = ("admin", "admin")
            url = "mongodb://%s:%s@%s:%s" % (credentials[0], credentials[1], ip, port)
            myclient = pymongo.MongoClient(url)
            try:
                myclient.list_database_names()
                return True, credentials
            except pymongo.errors.OperationFailure:
                return False, None
        else:
            return False, None
    except pymongo.errors.ServerSelectionTimeoutError:
        raise DatabaseConnectionError("no mongoDB instance found running at this address")


def redis_access_test(aggressive, ip, port):
    r = redis.Redis(ip, int(port))
    try:
        r.info("keyspace")
        return True, None
    except redis.exceptions.AuthenticationError:
        if aggressive:
            password = ["admin"]
            r1 = redis.StrictRedis(ip, int(port), password=password[0])
            try:
                r1.info("keyspace")
                return True, password
            except redis.exceptions.AuthenticationError:
                return False, None
        else:
            return False, None
    except redis.exceptions.ConnectionError:
        raise DatabaseConnectionError("no redis instance found running at this address")


mapping = {"redis": redis_access_test, "mongodb": mongodb_access_test, "rethinkdb": rethinkdb_access_test,
           "cassandradb": cassandra_access_test, "elasticsearch": elastic_access_test, "couchdb": couchdb_access_test}


def access_test(service, aggressive, ip, port):
    return mapping[service](aggressive, ip, port)


def automatic_discovery(nmap_file, ip, aggressive):
    result = {}
    open_ports = parse_nmap(nmap_file)
    database_ports = database_check(open_ports)
    for port in database_ports:
        result[port[0]] = (port[1], access_test(port[0], aggressive, ip, port[1]))
    return result
