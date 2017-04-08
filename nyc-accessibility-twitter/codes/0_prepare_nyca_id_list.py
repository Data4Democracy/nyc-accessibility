##############################
# This program reads in the nyca station data from 'elevator-pipeline', 
## and create a csv file with id, name, number of elevators, location, serving
## only need to be run once unless MTA starts to get more elevators
##############################

import pandas as pd
import json
import requests
import time

# read in all station details
nyca_stations = requests.get("http://www.nycaccessible.com/api/v1/stations/").json()
def get_nyca_station_detail(station_id):
    time.sleep(0.2) # Hack to avoid hitting API limits; should do exponential backoff here but too lazy
    detail = requests.get(
        "http://www.nycaccessible.com/api/v1/stations/{}.json".format(station_id)).json()
    return detail
all_nyca_station_details = {stn['id']:get_nyca_station_detail(stn['id']) for stn in nyca_stations}

json_df = pd.DataFrame(all_nyca_station_details).T

# keep only accessible stations
accessible_df = json_df[json_df['is_accessible'] == True].copy()

# if None make it as 0 Elevator
print("These elevators are marked as accessible, but has 0 elevators, may need investigation")
print(accessible_df.loc[accessible_df['elevator_count_words'].isnull()]) # elevator id (189, 279, 345, 348, 355, 425)
accessible_df.loc[accessible_df['elevator_count_words'].isnull(), 'elevator_count_words'] = '0 Elevators'

accessible_list = []
for i in range(accessible_df.shape[0]): 
    row = accessible_df.iloc[i]
    nyca_id = row['id']
    name = row['name']
    num_elevator = row['elevator_count_words'].split()[0]
    for item in row['machines']: 
        location = item['location']
        serving = item['serving']
        accessible_list.append([nyca_id, name, num_elevator, location, serving])

df = pd.DataFrame(accessible_list, columns = ['nyca_id', 'name', 'number_of_elevators', 'location', 'serving'])

df.to_csv('../data/nyca_id.csv', index = False)
