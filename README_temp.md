# equaeris
## TL;DR
equaeris is a modular scanner to find open databases and extract their content
## Description
equaeris is subdivided into two big modules, one for discovery and one for extraction. Based on the needs they can either be used by themselves or be combined. Right now the supported databases are MongoDB, redis, RethinkDB, CassandraDB, CouchDB and elasticsearch with an amazon s3 extractor nearly finished
## Example
Imagine a server that is running an open redis instance, a default password protected cassandraDB instance and a non-default password protected mongoDB instance.
Running automatic_discovery on aggressive mode and providing a nmap xml file to it would return a dictionary that
