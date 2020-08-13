import requests, os
import xml.etree.ElementTree as ET


def bucket_access_test(bucketname):
    url = "http://" + bucketname + ".s3.amazonaws.com/"
    r = requests.get(url)
    tree = ET.fromstring(r.text)
    if tree[0].text == "AccessDenied":
        return False
    elif tree[0].text == "NoSuchBucket":
        raise
    else:
        return True


def extract_bucket(bucketname, max_elements):
    count = 0
    path = os.path.dirname(__file__)
    url = "http://" + bucketname + ".s3.amazonaws.com/"
    r = requests.get(url)
    tree = ET.fromstring(r.text)
    if tree[0].text == "AccessDenied":
        raise
    elif tree[0].text == "NoSuchBucket":
        raise
    contents = tree[5:]
    for content in contents:
        for child in content:
            if "Key" in child.tag:
                file = child.text
                r1 = requests.get(url + file)
                abs_path = os.path.join(path, file)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, 'wb') as f:
                    f.write(r1.content)
                count += 1
                if count >= max_elements:
                    return


print(bucket_access_test("advent-bucket-one"))
