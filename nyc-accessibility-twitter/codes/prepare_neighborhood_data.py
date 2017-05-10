##############################
# prepare neighborhood data (takes about 5-10 minutes to run)
##############################

import json
import pickle
import requests
from shapely.geometry import asShape

### station data

# download MTA station data
with open('../data/mta_stations_sorted_by_name', 'rb') as file_obj: 
     mta_stations_sorted_by_name = pickle.load(file_obj)

# by object id
station_by_objectid = {
    s['properties']['objectid']: s
    for s in mta_stations_sorted_by_name}

# points
station_points_by_objectid = {
    s['properties']['objectid']: asShape(s['geometry'])
    for s in mta_stations_sorted_by_name}

### neighborhood data

# download data
neighborhood_json_url =  \
    'http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nynta/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson'
neighborhood_data = requests.get(neighborhood_json_url).json()

# by NTA Code
neighborhood_by_ntacode = {
    n['properties']['NTACode']: n
    for n in neighborhood_data['features']}

# polygons
neighborhood_polygons_by_ntacode = {
    n['properties']['NTACode']: asShape(n['geometry'])
    for n in neighborhood_data['features']}

### combine station and neighborhood data
i = 0
total = len(neighborhood_by_ntacode.keys())

def stations_in_neighborhood(ntacode):
    global i
    npoly = neighborhood_polygons_by_ntacode[ntacode]
    nname = neighborhood_by_ntacode[ntacode]['properties']['NTAName']
    
    #print("{i}/{total}: {nname}".format(i = i, total = total, nname = nname))
    i = i + 1
    
    return (ntacode, nname, [
        station_id # objectid
        for station_id, station_point in station_points_by_objectid.items()
        if npoly.contains(station_point)
    ])

neighborhood_to_stations = [
    stations_in_neighborhood(n_id)
    for n_id, n_detail in neighborhood_by_ntacode.items()
]

# go back to the original neighborhood data and populate it with 
## a count_of_stations property for graphing
neighborhood_to_count = {
    n_id: len(stations)
    for n_id, n_name, stations in neighborhood_to_stations
}

# enrich original neighborhood data geojson with count_of_subway_stations
for n in neighborhood_data['features']: 
    n_id = n['properties']['NTACode']
    n['properties']['count_of_subway_stops'] = neighborhood_to_count[n_id]

with open('../data/neighborhood_data', 'wb') as file_obj: 
     pickle.dump(neighborhood_data, file_obj)