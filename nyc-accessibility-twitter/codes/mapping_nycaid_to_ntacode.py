# We prepare the mapping of nyca id to nta code and pickle it 
# into '../data/nyca_station_to_ntacode', so that we don't have to do this multiple times
import pandas as pd
import math
import json
from collections import defaultdict
import pickle

json_path = '../../elevator-pipeline/data/'

dr1 = pd.read_csv('{}aligned_mta_nyca.csv'.format(json_path))
dr1.reset_index(drop = True, inplace = True)

# tuple of (mta,nyca_id)
def format_mta_id(flt):
    if not flt or math.isnan(flt):
        return None
    else:
        return str(int(flt))

def format_nyca_id(flt):
    if not flt or math.isnan(flt):
        return None
    else:
        return int(flt)

aligned_objectids = [
    (format_mta_id(dr1.iloc[i, 3]),format_nyca_id(dr1.iloc[i, 7]))
    for i in range(len(dr1))
]

with open('{}stations_to_neighborhoods.json'.format(json_path)) as infile:
    stations_to_neighborhoods = json.load(infile)

nyca_station_to_ntacode = defaultdict(lambda: set())
for mta_id, nyca_id in aligned_objectids:
    if mta_id is None:
        print('Missing mta_id for nyca_id {}'.format(nyca_id))
    elif nyca_id is None:
        print('Missing nyca_id for mta_id {}'.format(mta_id))
        
    elif mta_id in stations_to_neighborhoods:
        neighborhoods = stations_to_neighborhoods[mta_id]
        if len(neighborhoods) == 1:
            nyca_station_to_ntacode[nyca_id].add(neighborhoods[0])
        else:
            print('Multi-neighborhood data for {}/{}'.format(mta_id,nyca_id))
    else:
        print('Missing neighborhood data for {}'.format(mta_id))

# turn defaultdict to regular dict
nyca_station_to_ntacode = dict(nyca_station_to_ntacode)

with open('../data/nyca_station_to_ntacode', 'wb') as file_obj: 
     pickle.dump(nyca_station_to_ntacode, file_obj)