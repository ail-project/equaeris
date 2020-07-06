import xml.etree.ElementTree as ET
import json
import pexpect
import time


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
    if instructions["inputstart"] != "":
        p.expect(instructions["inputstart"])
    for command in instructions["authcheck"][0]:
        p.sendline(command)
        p.expect(command)
        p.expect(instructions["authcheck"][1])
    authcheck = p.before.decode()
    if instructions["authcheck_fail"] != "":
        if instructions["authcheck_fail"] not in authcheck:
            return True, None
        elif not aggressive:
            return False, None
        else:
            return client_aggressive_access(instructions, p)
    elif instructions["authcheck_success"] != "":
        if instructions["authcheck_success"] in authcheck:
            return True, None
        elif not aggressive:
            return False, None
        else:
            return client_aggressive_access(instructions, p)


def client_aggressive_access(instructions, p):
    for command in instructions["aggressive"][0]:
        if "%u" in command:
            command = command.replace("%u", "\"admin\"")
        if "%p" in command:
            command = command.replace("%p", "\"admin\"")
        p.sendline(command)
    for i in range(len(instructions["aggressive"][0])):
        p.expect(instructions["aggressive"][1])
    authcheck = p.before.decode()
    if instructions["aggressive_fail"] != "":
        if instructions["aggressive_fail"] not in authcheck:
            return True, ("admin","admin")
        else:
            return False, None
    elif instructions["aggressive_success"] != "":
        if instructions["aggressive_success"] in authcheck:
            return True, ("admin","admin")
        else:
            return False, None


def command_access_test(instructions, aggressive, ip, port):
    pass


def access_test(service, aggressive, ip, port):
    with open(service + "_access.json", 'r') as json_file:
        json_data = json_file.readline()
        instructions = json.loads(json_data)
    if instructions["client"]:
        return client_access_test(instructions, aggressive, ip, port)
    else:
        command_access_test(instructions, aggressive, ip, port)


liste = parse_nmap("nmap.xml")
database_check(liste)

print(access_test("mongoDB", True, "127.0.0.1", "27017"))
