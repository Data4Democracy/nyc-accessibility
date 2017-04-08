import pandas as pd
import json
from aux_func.analysis_func \
    import station_scores_to_neighborhood_data, create_map_input

# read in twitter data
df = pd.read_csv('../data/cleaned_nyc_accessible_twitter_data.csv', parse_dates = [5, 7])

# ### create json file for mean time spent for fixing
# # prepare dictionary at station level
time_spent_df = df[['nyca_id', 'time_spent_min']].groupby('nyca_id').mean()
time_spent_dict = time_spent_df.to_dict()['time_spent_min']

# create a json for map
create_map_input(time_spent_dict, 'mean_time_spent')

### create json file for number of elevators
# prepare dictionary at station level
#df['number_of_elevators'] = df['number_of_elevators'].astype(int)
num_elev_df = df[['nyca_id', 'number_of_elevators']].groupby('nyca_id').mean()
num_elev_dict = num_elev_df.to_dict()['number_of_elevators']

# create a json for map
create_map_input(num_elev_dict, 'mean_elev_num')
