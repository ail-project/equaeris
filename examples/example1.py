import discovery
import extraction

ip = "127.0.0.1"

databases = discovery.automatic_discovery("nmap.xml",ip,True)
print(databases)
for pair in databases:
    database = databases[pair]
    if(database[1][0]):
        output = extraction.extract_database(pair,ip,database[0],database[1][1])
        outputfile = pair + ".out"
        extraction.dump_contents(output,outputfile)