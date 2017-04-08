##############################
# download MTA geo data from NYC open data API, 
## sort it by name, and pickle the dictionary 
## need to be done only once unless there's a significance in NYC subway system
##############################
import requests
import pickle

station_geo = requests.get(
    'https://data.cityofnewyork.us/api/geospatial/arq3-7z49?method=export&format=GeoJSON').json()
mta_stations_sorted_by_name = \
    sorted(station_geo['features'], key = lambda r: r['properties']['name'])

with open('../data/mta_stations_sorted_by_name', 'wb') as file_obj: 
     pickle.dump(mta_stations_sorted_by_name, file_obj)