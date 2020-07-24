import rethinkdb


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


def extract_rethinkdb(ip, port, credentials=None):
    result = {}
    r = rethinkdb.RethinkDB()
    if credentials is not None:
        r.connect(ip, int(port), user=credentials[0], password=credentials[1]).repl()
    else:
        r.connect(ip, int(port)).repl()
    databases = r.db_list().run()
    for database in databases:
        if database != "rethinkdb":
            result[database] = {}
            tables = r.db(database).table_list().run()
            for table in tables:
                result[database][table] = []
                cursor = r.db(database).table(table).run()
                for doc in cursor:
                    result[database][table].append(doc)
    return result


print(extract_rethinkdb("127.0.0.1", "28015", ("admin", "admin")))
