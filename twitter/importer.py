# Library
import json
import argparse
import pycouchdb
import csv
from cloudant.client import CouchDB
import setting as cf

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, dest='filename', default='./aurin.json', help='Choose the json file to import into couchDB')
    parser.add_argument('--db', type=str, dest='database', default='aurin', help='Choose the database to import the data into')
    parser.add_argument('--type', type=str, dest='fileType', default='csv', help='Choose the file type (csv/json)')
    args = parser.parse_args()

    client = CouchDB(cf.db_user, cf.db_password, url='http://{}:{}'.format(cf.db_host, cf.db_port), connect=True)
    db = client[args.database]

    with open(args.filename) as f:
        if args.fileType == 'json':
            data = json.load(f)
        elif args.fileType == 'csv':
            data = csv.DictReader(f, delimiter=',')
            for x in data:
                create_document = db.create_document(x)

    if args.fileType == 'json':
        for x in data["features"]:
            create_document = db.create_document(x)