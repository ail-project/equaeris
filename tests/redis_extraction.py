import redis


def extract_redis(ip, port, password=None):
    print(ip,port,password)


    if password is not None:
        r = redis.StrictRedis(ip, int(port), password=password[0])
    else:
        r = redis.Redis(ip, int(port))
    try:
        keyspace = r.info("keyspace")
    except redis.exceptions.AuthenticationError:
        print("database requires authentication")
        return
    for space in keyspace:
        print(space)

        if password is not None:
            r1 = redis.StrictRedis(ip, int(port), int(space[-1]), password=password[0])
        else:
            r1 = redis.Redis(ip, int(port), int(space[-1]))

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
                print(r1.lrange(key, 0, -1))
            elif realm == b"set":
                print(key.decode() + ":", end="")
                print(r1.smembers(key))
            elif realm == b"zset":
                print(key.decode() + ":", end="")
                print(r1.zrange(key, 0, -1))


extract_redis("127.0.0.1", "6379",["admin"])
