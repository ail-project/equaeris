from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"])
session = cluster.connect(keyspace="tutorialspoint")
print(cluster.metadata.keyspaces)
keyspace = cluster.metadata.keyspaces["tutorialspoint"]
print(keyspace.tables)
rows = session.execute('Select * from emp')
for row in rows:
    print(row)
