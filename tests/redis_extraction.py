import pexpect

p = pexpect.spawn("redis-cli --raw -h 127.0.0.1 -p 6379")
p.send("keys *".encode())
p.sendcontrol('m')
p.expect("127.0.0.1:6379")
p.expect("127.0.0.1:6379")
p.expect("127.0.0.1:6379")
p.expect("127.0.0.1:6379")


print(p.before)
