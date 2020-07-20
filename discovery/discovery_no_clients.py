import xml.etree.ElementTree as ET
import json
import pymongo
import redis
import requests
from requests.auth import HTTPBasicAuth


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
    with open('ports.json', 'r') as json_file:
        json_data = json_file.readline()
        db_ports = json.loads(json_data)
        for port in open_ports:
            if port in db_ports:
                print("Open", db_ports[port], "at port", port)


def mongodb_access_test(aggressive, ip, port):
    url = "mongodb://%s:%s" % (ip, port)
    myclient = pymongo.MongoClient(url)
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


def url_access_test(instructions, aggressive, ip, port):
    url = instructions["start"]
    if "%ip" in url:
        url = url.replace("%ip", ip)
    if "%port" in url:
        url = url.replace("%port", port)
    print(url)
    url += instructions["authcheck"][0]
    r = requests.get(url)
    if instructions["authcheck_fail"] != "":
        if instructions["authcheck_fail"] in r.json():
            if aggressive:
                return url_aggressive_access(instructions, ip, port)
            else:
                return False, None

        else:
            return True, None

    elif instructions["authcheck_success"] != "":
        if instructions["authcheck_success"] in r.json():
            return True, None
        else:
            if aggressive:
                return url_aggressive_access(instructions, ip, port)
            else:
                return False, None


def url_aggressive_access(instructions, ip, port):
    url = instructions["aggressive"][0]
    if "%ip" in url:
        url = url.replace("%ip", ip)
    if "%port" in url:
        url = url.replace("%port", port)
    if "%u" in url:
        url = url.replace("%u", "admin")
    if "%p" in url:
        url = url.replace("%p", "admin")
    if instructions["basic_auth"]:
        r = requests.get(url, auth=HTTPBasicAuth('elastic', 'elastic'))
    else:
        r = requests.get(url)
    if instructions["aggressive_fail"] != "":
        if instructions["aggressive_fail"] in r.json():
            return False, None
        else:
            return True, ("admin", "admin")

    elif instructions["aggressive_success"] != "":
        if instructions["aggressive_success"] in r.json():
            return True, ("admin", "admin")
        else:
            return False, None


mapping = {"redis": redis_access_test, "mongoDB": mongodb_access_test}


def access_test(service, aggressive, ip, port):
    with open("access.json", 'r') as json_file:
        json_data = json_file.readline()
        data = json.loads(json_data)
        instructions = data[service]
    if instructions["client"]:
        return mapping[service](aggressive, ip, port)
    else:
        return url_access_test(instructions, aggressive, ip, port)


liste = parse_nmap("nmap.xml")
database_check(liste)

print(access_test("mongoDB", False, "127.0.0.1", "27017"))
print(access_test("redis", False, "127.0.0.1", "6379"))
print(access_test("mongoDB", True, "127.0.0.1", "27017"))
print(access_test("redis", True, "127.0.0.1", "6379"))
print(access_test("elastic", True, "127.0.0.1", "9200"))
print(access_test("elastic", False, "127.0.0.1", "9200"))
print(access_test("couchDB", True, "127.0.0.1", "5984"))
print(access_test("couchDB", False, "127.0.0.1", "5984"))
