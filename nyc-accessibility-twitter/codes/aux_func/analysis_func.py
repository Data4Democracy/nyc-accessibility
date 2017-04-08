import pandas as pd
import json
import pickle

from collections import defaultdict

json_path = '../../elevator-pipeline/data/'

def station_scores_to_neighborhood_data(station_msr_dict):
    """
    Parameters
    ----------
    station_msr: dictionary
        dictionary with nyca station id and corresponding scores

    Returns
    ----------
    neighborhood_mean_msr: dictionary
        dictionary with neighboarhood code and corresponding scores
    """
    # read in pickled mapping of nyca id to nta code
    with open('../data/nyca_station_to_ntacode', 'rb') as file_obj: 
         nyca_station_to_ntacode = pickle.load(file_obj)

    # get the average of the measure across the neighborhood 
    neighborhood_scores = {}
    for station_id, station_score in station_msr_dict.items():

        for neighborhood in nyca_station_to_ntacode[int(station_id)]:
            if neighborhood not in neighborhood_scores: 
                neighborhood_scores[neighborhood] = {}
                neighborhood_scores[neighborhood]['num_station'] = 1
                neighborhood_scores[neighborhood]['total_msr'] = station_score

            else: 
                neighborhood_scores[neighborhood]['num_station'] += 1
                neighborhood_scores[neighborhood]['total_msr'] += station_score

    neighborhood_mean_msr = {}
    for neighborhood in neighborhood_scores.keys():
        neighbor_vals = neighborhood_scores[neighborhood]
        neighborhood_mean_msr[neighborhood] = \
            neighbor_vals['total_msr'] / neighbor_vals['num_station']

    return neighborhood_mean_msr

# create json file for map input
# enrich the original neighborhood_data geojson with neighborhood_score
def create_map_input(station_scores_dict, msr_name): 
    """
    Parameters 
    ----------
    station_scores_dict: dictionary
    msr_name: string
        name of neighborhood scores (this will be used in the json data and used for map)

    Returns
    ----------
    json file
        with 'output_name' as file name
    """
    with open('{}neighborhood_data.json'.format(json_path)) as infile:
        neighborhood_data = json.load(infile)

        # prepare the dictionary at neighborhood level
        neighborhood_scores = station_scores_to_neighborhood_data(station_scores_dict)

    for n in neighborhood_data['features']:
        n_id = n['properties']['NTACode']
        n['properties'][msr_name] = neighborhood_scores.get(n_id,0)

    with open('../map_input/{}.json'.format(msr_name),'w') as outfile:
        json.dump(neighborhood_data, outfile)