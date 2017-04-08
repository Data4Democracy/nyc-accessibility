import pandas as pd
import re

from aux_func.cleaning_func \
    import clean_text_column, combine_continuing_tweets, pair_outage_fix

### Read in data
df = pd.read_csv('../../data/nycoutages_tweets.csv')
df.reset_index(drop = True, inplace = True)

### clean the data

# clean the column with date
df.rename(columns = {'tweet_id': 'date'}, inplace = True)
df['date_date'] = pd.to_datetime(df['date'])
df.drop('date', axis = 1, inplace = True)
df.rename(columns = {'date_date': 'date'}, inplace = True)

# split 'text' column to 'status', 'human_eq_type', 'name', 'serving' and 'location'
df = clean_text_column(df)

# keep only 'elevator' (remove escalator)
df = df[df['human_eq_type'] != 'An escalator']

# Combine 'that elevator' record with the main record
df = combine_continuing_tweets(df)

# drop if no name (nothing much we could do about this)
pct_no_name = df[df.name == ''].shape[0] / df.shape[0] * 100
print("Dropping {:.0f}% of data because of no name".format(pct_no_name))
df = df[df['name'] != '']

### pair up OUTAGE and FIXED for the same elevator
df = pair_outage_fix(df)

# set date/time as date format 
df['date2'] = pd.to_datetime(df['date2'])

# calculate time spent for fixing in minutes
df['time_spent_min'] = (df['date2'] - df['date']).fillna(0).apply(lambda x: x.seconds / 60).astype(int)

# top code time spent at 600
df['time_spent_min'] = df['time_spent_min'].apply(lambda x: min(x, 600))
df.loc[(df['status2'] != 'FIXED') & (df['time_spent_min'] == 0), 'time_spent_min'] = 600
print("Note: 'time_spent_min' is top-coded at 600, 600 includes 'not fixed'")

### merge in nyca_id
id_df = pd.read_csv('../data/nyca_id.csv').fillna('')
df = df.merge(id_df, on = ['name', 'location', 'serving'])

# export data
df.to_csv('../data/cleaned_nyc_accessible_twitter_data.csv', index = False)
