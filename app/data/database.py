# -*- coding: utf-8 -*-
# Library
# File
import setting.config as config
from cloudant.client import CouchDB
from cloudant.query import Query


def connectDatabase(database):
    client = CouchDB(config.db_user, config.db_password, url='http://{}:{}'.format(config.db_host, config.db_port),
                     connect=True)
    db = client[database]
    return db


# Search view for text
def getText(query, view_type, language="en"):
    # Connect to the database
    db = connectDatabase('twitter')

    # Filter language
    language_list = ["en", "ar", "zh", "es", "hi", "th", "ja"]

    # Query result
    if language in language_list:
        result = db.get_view_result('_design/text_{}'.format(language), view_type, key="{}".format(query))
    else:
        result = db.get_view_result('_design/text_all', view_type, key="{}".format(query))

    # Variable
    value = []

    # Set variable to check if database is empty
    check_list = list(result)

    # Return value if the return value is empty
    if not check_list:
        message = "Error: Does not find the value requested"
        return message

    # Parse data to value and return
    else:
        for i in result:
            # For search type = date
            if view_type == "date":
                # Variable
                text = ""
                location = ""
                date = ""

                # Store text if extended tweet is not empty
                if i["value"][2] != "":
                    text = i["value"][2]

                # Store text if extended tweet is empty
                elif i["value"][2] == "":
                    text = i["value"][1]

                # Store other value
                date = i["key"]
                location = i["value"][0]

                # Store value
                value.append({"date": date, "text": text, "location": location})

            # For search type = place
            elif view_type == "place":
                # Variable
                text = ""
                location = ""

                # Store text if extended tweet is not empty
                if i["value"][1] != "":
                    text = i["value"][1]

                # Store text if extended tweet is empty
                elif i["value"][1] == "":
                    text = i["value"][0]

                # Store other value
                location = i["key"]

                # Store value
                value.append({"location": location, "text": text})

        return value


def getLifeExpectancy(query=None, by='name'):
    # Connect to the database
    db = connectDatabase('aurin')

    # Send query to get all the value from aurin
    if query == None:
        data = Query(db, selector={'_id': {'$gt': 0}})
    else:
        if by == 'name':
            data = Query(db, selector={'gccsa_name': '{}'.format(query)})
        elif by == 'code':
            data = Query(db, selector={'feature_code': '{}'.format(query)})
        else:
            message = "Error: This search method does not exist"
            return message

    if not data:
        message = "Result: no data found in the database that match with the query"
        return message

    return data.result[:]


def getCity(city, state):
    # Connect to the database
    db = connectDatabase('city')

    # Send query to get all specific value from city
    data = Query(db, selector={'town': '{}'.format(city), 'state': '{}'.format(state)})

    if not data:
        message = "Result: no data found in the database that match with the query"
        return message

    return data.result[:]
