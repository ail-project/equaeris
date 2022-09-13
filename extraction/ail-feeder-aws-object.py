#!/usr/bin/env python3
# -*-coding:UTF-8 -*

import argparse
import configparser
import os
import json
import sys

from pyail import PyAIL
import extraction

config = configparser.ConfigParser()
config.read('../etc/conf.cfg')

if not 'AIL' in config:
    print('Config error')
    sys.exit(0)
else:
    ail_url = config.get('AIL', 'url')
    ail_key = config.get('AIL', 'apikey')
    verifycert = config.getboolean('AIL', 'verifycert')
    connect = False
    pyail = None
    try:
        feeder_uuid = config.get('AIL', 'feeder_uuid')
    except Exception as e:
        feeder_uuid = 'aae656ec-d446-4a21-acf0-c88d4e09d509'

    try:
        pyail = PyAIL(ail_url, ail_key, ssl=verifycert)
    except Exception as e:
        print(e)
        sys.exit(0)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='AIL AWS Object feeder')
    parser.add_argument('-b', '--bucket',help='aws bucket name' , type=str, dest='bucket', default=None, required=True)
    parser.add_argument('-o', '--object',help='aws object name' , type=str, dest='object', default=None, required=True)
    args = parser.parse_args()

    # # TODO: ADD Channel monitoring
    if not args.bucket and not args.object:
        parser.print_help()
        sys.exit(0)

    data = extraction.extract_aws_s3_object(args.bucket, args.object)
    dict_meta = {'bucket': args.bucket, 'object': args.object}
    pyail.feed_json_item(data.decode(), dict_meta, 'ail_feeder_aws_object', feeder_uuid)
