import pexpect

p = pexpect.spawn("mongo")
p.send("show dbs".encode())
p.sendcontrol('m')
try:
    p.expect("admin",timeout = 3)
except:
    print("port is open")
