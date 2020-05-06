# Library
import json
import pandas as pd

if __name__ == '__main__':
    # Variable
    sa1_prop = []
    sa1_geo = []

    # Output
    filter_layer = {}
    filter_layer["features"] = []
    output = {}
    output["features"] = []

    # Load geojson
    with open ('sa1.geojson', mode='r') as sa1:
        sa1_data = json.load(sa1)
        for i in sa1_data["features"]:
            sa1_prop.append(i["properties"])
            sa1_geo.append(i["geometry"])

    # Load csv
    df = pd.read_csv("sa1_data.csv")

    # Match data between the two
    for count, i in enumerate(sa1_prop):
        search = i["sa1_main16"]
        search_csv = df['SA1_MAINCODE_2016'] == int(search)
        matching = df[search_csv]
        # Generate new json format
        filter_layer["features"].append({
            'properties': {
                'sa2_name': matching['SA2_NAME_2016'].item(),
                'sa3_name': matching['SA3_NAME_2016'].item(),
                'sa4_name': matching['SA4_NAME_2016'].item(),
                'gccsa_name_2016': matching['GCCSA_NAME_2016'].item(),
                'state_name_2016': matching['STATE_NAME_2016'].item(),
                'geometry': {
                    "bbox": sa1_geo[count]["bbox"],
                    "type": sa1_geo[count]["type"],
                    "coordinates": sa1_geo[count]["coordinates"]
                }
            }
        })

    # # Store unique suburbs
    # unique = []

    # for i in filter_layer["features"]:
    #     if i["properties"]['SA2_NAME'] not in unique:
    #         unique.append({
    #             'sa2_name': i["properties"]['SA2_NAME'], 
    #             'sa3_name': i["properties"]['SA3_NAME'],
    #             'sa4_name': i["properties"]['SA4_NAME'],
    #             'gccsa_name_2016': i["properties"]['GCCSA_NAME_2016'],
    #             'state_name_2016': i["properties"]['STATE_NAME_2016'],
    #         })

    # for i in unique:
    #     total_coordinates = []
    #     bbox = []
    #     xmin = 200
    #     xmax = 0
    #     ymin = 0
    #     ymax = -200
    #     for count, x in enumerate(filter_layer["features"]):
    #         if i["sa2_name"] == x["properties"]["SA2_NAME"]:
    #             for d in x["properties"]["geometry"]["coordinates"]:
    #                 total_coordinates += d 
    #             if x["properties"]["xmax"] >= xmax:
    #                 xmax = x["properties"]["xmax"]
    #             if x["properties"]["xmin"] <= xmin:
    #                 xmin = x["properties"]["xmin"]
    #             if x["properties"]["ymax"] >= ymax:
    #                 ymax = x["properties"]["ymax"]
    #             if x["properties"]["ymin"] <= ymin:
    #                 ymin = x["properties"]["ymin"]
    #     output["features"].append({
    #         'properties': {
    #             'sa2_name': i["sa2_name"],
    #             'sa3_name': i["sa3_name"],
    #             'sa4_name': i["sa4_name"],
    #             'gccsa_name_2016': i["gccsa_name_2016"],
    #             'state_name_2016': i["state_name_2016"],
    #             'geometry': {
    #                 "bbox": [xmin, ymin, xmax, ymax],
    #                 "type": sa1_geo[count]["type"],
    #                 "coordinates": total_coordinates
    #             }
    #         }
    #     })   

    # Export the file
    with open('aurin.json', 'w') as aurin:
        # json.dump(output, aurin)
        json.dump(filter_layer, aurin)