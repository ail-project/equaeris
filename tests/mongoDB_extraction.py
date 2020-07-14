import pymongo


def extract_mongodb(ip, port, credentials=None):
    if credentials is not None:
        url = "mongodb://%s:%s@%s:%s" % (credentials[0], credentials[1], ip, port)
    else:
        url = "mongodb://%s:%s" % (ip, port)

    myclient = pymongo.MongoClient(url)
    try:
        databases = myclient.list_database_names()
    except pymongo.errors.OperationFailure:
        print("database requires authentication")
        return
    for database in databases:
        if database not in ["admin", "config", "local"]:
            db = myclient[database]
            collections = db.list_collection_names()
            for collection in collections:
                print(collection)
                col = db[collection]
                for x in col.find():
                    print(x)


extract_mongodb("127.0.0.1", "27017")
