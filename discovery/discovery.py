import xml.etree.ElementTree as ET
import json
import pexpect
import time
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


def client_access_test(instructions, aggressive, ip, port):
    process = instructions["start"]
    if "%ip" in process:
        process = process.replace("%ip", ip)
    if "%port" in process:
        process = process.replace("%port", port)
    print(process)
    p = pexpect.spawn(process)
    time.sleep(1)

    for command in instructions["authcheck"]:
        p.send(command.encode())
        p.sendcontrol('m')
    if instructions["authcheck_fail"] != "":
        try:
            p.expect(instructions["authcheck_fail"], timeout=2)
            if aggressive:
                return client_aggressive_access(instructions, p)
            else:
                return False, None

        except pexpect.exceptions.TIMEOUT:
            return True, None

    elif instructions["authcheck_success"] != "":
        try:
            p.expect(instructions["authcheck_success"], timeout=2)
            return True, None
        except pexpect.exceptions.TIMEOUT:
            if aggressive:
                return client_aggressive_access(instructions, p)
            else:
                return False, None


def client_aggressive_access(instructions, p):
    result = []
    for command in instructions["aggressive"]:
        if "%u" in command:
            command = command.replace("%u", "\"admin\"")
            result.append("admin")
        if "%p" in command:
            command = command.replace("%p", "\"admin\"")
            result.append("admin")
        p.send(command.encode())
        p.sendcontrol('m')

    if instructions["aggressive_fail"] != "":
        try:
            p.expect(instructions["aggressive_fail"], timeout=2)
            return False, None
        except pexpect.exceptions.TIMEOUT:
            return True, result

    elif instructions["aggressive_success"] != "":
        try:
            p.expect(instructions["aggressive_success"], timeout=2)
            return True, result
        except pexpect.exceptions.TIMEOUT:
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
        r = requests.get(url, auth=HTTPBasicAuth('elastic','elastic'))
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


def access_test(service, aggressive, ip, port):
    with open("access.json", 'r') as json_file:
        json_data = json_file.readline()
        data = json.loads(json_data)
        instructions = data[service]
    if instructions["client"]:
        return client_access_test(instructions, aggressive, ip, port)
    else:
        return url_access_test(instructions, aggressive, ip, port)


liste = parse_nmap("nmap.xml")
database_check(liste)

#print(access_test("mongoDB", False, "127.0.0.1", "27017"))
print(access_test("redis", False, "127.0.0.1", "6379"))
#print(access_test("mongoDB", True, "127.0.0.1", "27017"))
print(access_test("redis", True, "127.0.0.1", "6379"))
print(access_test("elastic", True, "127.0.0.1", "9200"))
print(access_test("elastic", False, "127.0.0.1", "9200"))
print(access_test("couchDB", True, "127.0.0.1", "5984"))
print(access_test("couchDB", False, "127.0.0.1", "5984"))

