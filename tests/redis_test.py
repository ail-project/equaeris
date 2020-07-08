import pexpect

p = pexpect.spawn("redis-cli -h 127.0.0.1 -p 6379")
p.send("keys *".encode())
p.sendcontrol('m')
try:
    p.expect("NOAUTH",timeout = 3)
    print("Success")
except:
    print("port is open")

p.send("AUTH admin".encode())
p.sendcontrol('m')
try:
    p.expect("OK",timeout = 2)
    print("Success")
except:
    print("Fail")
