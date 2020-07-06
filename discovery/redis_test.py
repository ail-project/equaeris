import pexpect

p = pexpect.spawn("redis-cli")
p.send("keys *".encode())
p.sendcontrol('m')
try:
    p.expect("NOAUTH",timeout = 3)
except:
    print("port is open")
