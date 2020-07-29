import cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


def cassandra_access_test(aggressive, ip, port):
    cluster = Cluster([ip], port=port)
    try:
        cluster.connect()
        return True, None
    except cassandra.cluster.NoHostAvailable:
        if not aggressive:
            return False, None
        else:
            auth = PlainTextAuthProvider("cassandra", "cassandra")
            cluster = Cluster([ip], port=int(port), auth_provider=auth)
            try:
                cluster.connect()
                return True, ("cassandra", "cassandra")
            except cassandra.cluster.NoHostAvailable:
                return False, None


def extract_cassandra(ip, port, credentials=None):
    result = {}
    if credentials is None:
        cluster = Cluster([ip], port=port)
    else:
        auth = PlainTextAuthProvider(credentials[0], credentials[1])
        cluster = Cluster([ip], port=port, auth_provider=auth)
    cluster.connect()
    for keyspace in cluster.metadata.keyspaces:
        if "system" not in keyspace:
            result[keyspace] = {}
            session = cluster.connect(keyspace=keyspace)
            session.row_factory = cassandra.query.dict_factory
            act_keyspace = cluster.metadata.keyspaces[keyspace]
            for table in act_keyspace.tables:
                result[keyspace][table] = []
                cql = 'Select * from ' + table
                rows = session.execute(cql)
                for row in rows:
                    result[keyspace][table].append(row)
    return result


print(cassandra_access_test(True, "127.0.0.1", "9042"))
print(extract_cassandra("127.0.0.1", "9042", ["cassandra", "cassandra"]))
