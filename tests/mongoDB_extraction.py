import pymongo

def extract_mongoDB(ip,port,credentials = None):
    if credentials != None:
        url = "mongodb://%s:%s@%s:%s" % (credentials[0],credentials[1],ip,port)
    else:
        url = "mongodb://%s:%s" % (ip,port)

    myclient = pymongo.MongoClient(url)
    databases = myclient.list_database_names()
    for database in databases:
        if database not in ["admin","config","local"]:
            db = myclient[database]
            collections = db.list_collection_names()
            for collection in collections:
                col = db[collection]
                for x in col.find():
                    print(x)

extract_mongoDB("127.0.0.1","27017")
