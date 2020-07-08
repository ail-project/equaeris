import requests

r = requests.get('http://127.0.0.1:5984/_all_dbs')
data = r.json()
if "error" in data:
    print("Success")
    print(data["error"])
