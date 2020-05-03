# Library
import json
import argparse
import pycouchdb
import setting as cf

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--array', type=str, dest='array', default='features', help='the array part of the json that you want to import')
    parser.add_argument('--filename', type=str, dest='filename', default='./spartialise-data.json', help='Choose the json file to import into couchDB')
    parser.add_argument('--db', type=str, dest='database', default='aurin', help='Choose the database to import the data into')
    args = parser.parse_args()

    with open(args.filename) as f:
        data = json.load(f)

    server = pycouchdb.Server("http://{}:{}@localhost:{}/".format(cf.db_user, cf.db_password, cf.db_port))
    db = server.database(args.database)
    db.save_bulk(data[args.array])