# equaeris
## TL;DR
equaeris is a modular scanner to find open databases and extract their content
## Description
equaeris is subdivided into two big modules, one for discovery and one for extraction. Based on the needs they can either be used by themselves or be combined. Right now the supported databases are MongoDB, redis, RethinkDB, CassandraDB, CouchDB, elasticsearch and amazon s3.
## Example
### Discovery
Imagine a server that is running an open mongoDB instance, a default password protected cassandraDB instance and a non-default password protected redis instance. To check which databases are open and unprotected, you can either use automatic_discovery() when you already have a nmap xml file or call the individual database access functions.
#### automatic_discovery()
Running automatic_discovery on aggressive mode and providing a nmap xml file to it would return a dictionary that contains the scan results. In this case, the resulting dictionary would look like this:
```python
{'redis': ('6379', (False, None)), 'cassandradb': ('9042', (True, ('cassandra', 'cassandra'))), 'mongodb': ('27017', (True, None))}
```
This is simply achieved by calling this function:
```python
automatic_discovery('nmap.xml',"IP", True)
 ```
 #### specific access functions
 Another way to achieve this result would be to call the specific access functions individually:
 ```python
redis_access_test(True,"IP","port")
mongodb_access_test(True,"IP","port")
cassandradb_access_test(True,"IP","port")
```
In this case, each function returns a tuple where the first element is either True or False based on whether access to the database has been achieved and the second element contains the potential credentials with which the access has been achieved.
Example for a default password protected cassandraDB instance:
```python
(True, ('cassandra', 'cassandra'))
```
### Extraction
To extract the content of a specific database you can either call the generic extract_database function or one of the specific functions geared towards each database. The extract_database function will print a snapshot of the first few key:value pairs of each database.

#### extract_database()
Going with the example from before, let's extract the contents of the unsecured mongoDB instance and the secured cassandraDB instance:
```python
res = extract_database("mongodb","IP","port")  
dump_contents(res,"mongoDB.json")  
res1 = extract_database("cassandradb","IP","port",["cassandra","cassandra"])  
dump_contents(res1,"cassandraDB.json")
```
res and res1 are dictionaries containing a representation of the databases. dump_contents() writes them to a json file for further investigation.
#### specific functions
You can also use extract_cassandra() and extract_mongodb() with the same parameters to extract the database contents.

### Discovery and Extraction together
If you want to extract everything from every open database on a server, and put the result into json files, you can use this script to achieve this:
```python
import discovery  
import extraction  
  
ip = "127.0.0.1"  
  
databases = discovery.automatic_discovery("nmap.xml",ip,True)  
for pair in databases:  
    database = databases[pair]  
    if database[1][0]:  
        output = extraction.extract_database(pair,ip,database[0],database[1][1])  
        outputfile = pair + ".json"  
	extraction.dump_contents(output,outputfile)
```

## Extension
The project can be easily extended by writing either discovery or extraction functions for certain database services.
After putting them into their respective scripts, update the mapping dictionary to let it point to the correct function.
An access_test function should always return the same format (boolean access_achieved, list of strings credentials or None if no credentials are needed).
An extraction function should simply return a dictionary that represents the database.

## Issues
The default value for max_elements for the extraction functions is 5000 and should work fine. If you want to extract more elements, there is a possibility that memory will fill up and the program will crash. I haven't tested it yet on really big databases so if that happens, try to decrease the max_elements parameter until it works.

## Dependencies
The scripts require python drivers for the databases that they exploit except for elasticsearch and couchDB where the requests library is required.



