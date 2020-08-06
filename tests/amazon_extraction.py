import requests
import xml.etree.ElementTree as ET


def extract_bucket(bucketname):
    url = "http://" + bucketname + ".s3.amazonaws.com/"
    r = requests.get(url)
    tree = ET.fromstring(r.text)
    contents = tree[5]
    for child in contents:
        if "Key" in child.tag:
            file = child.text
            r1 = requests.get(url + file)
            print(file , ":" , r1.text)
extract_bucket("ims-photos")
