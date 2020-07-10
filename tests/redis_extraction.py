import redis

r = redis.Redis("127.0.0.1",6379)
keyspace = r.info("keyspace")
for space in keyspace:
    print(space)
    r1 = redis.Redis("127.0.0.1",6379,int(space[-1]))
    keys = r1.keys("*")
    for key in keys:
        realm = r1.type(key)
        if realm == b"string":
            print(key.decode() + ":" + r1.get(key).decode())
        elif realm == b"hash":
            print(key.decode() + ":", end="")
            print(r1.hgetall(key))
        elif realm == b"list":
            print(key.decode() + ":", end="")
            print(r1.lrange(key,0,-1))
        elif realm == b"set":
            print(key.decode() + ":", end="")
            print(r1.smembers(key))
        elif realm == b"zset":
            print(key.decode() + ":", end="")
            print(r1.zrange(key,0,-1))
