import pandas as pd
import re

def clean_text_column(df):
    """
    split 'text' column into 'status', 'human_eq_type', 'name', 'serving', and 'location'

    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame with 'text' column

    Returns
    ----------
    df: pandas.DataFrame
        DataFrame with 'status', 'human_eq_type', 'name', 'serving' and 'location'
    """

    ### split 'text' column into 'status' and 'desc'
    # write a function
    def take_status(txt):
        txt_split = txt.split(': ')
        if len(txt_split) == 1: 
            status = ''
            desc = txt
        else: 
            status = txt_split[0]
            desc = txt_split[1]
        return status, desc

    # take out whether FIXED or OUTAGE
    df['status'] = df['text'].apply(lambda x: take_status(x)[0])

    # take out the description
    df['desc'] = df['text'].apply(lambda x: take_status(x)[1])

    # remove the last part ('is...') from 'desc' 
    def remove_ending(txt):
        end = txt.split(' is ')
        if len(end) > 1: 
            return end[0]
        else: 
            return txt
    df['desc'] = df['desc'].apply(lambda x: remove_ending(x).strip())

    ### split 'desc' column into 'human_eq_type', 'name', 'serving', 'location'

    # 'human_eq_type'
    def take_eq_type(txt):
        txt_split = txt.split(' ')
        if (txt[:1] == 'A') | (txt[:1] == 'T'):
            eq_type = txt_split[0] + ' ' + txt_split[1]
        else: 
            eq_type = ''
        return eq_type
    df['human_eq_type'] = df['desc'].apply(take_eq_type)

    ### take name, servicing, location
    def take_name(txt):
        name = txt.split('@')
        if len(name) > 1: 
            return name[0].strip(), name[1].strip()
        else: 
            return txt, ''

    def take_svc(txt):
        src_word = ''
        if re.search('servicing', txt):
            src_word = 'servicing'
        elif re.search('services', txt):
            src_word = 'services'

        if src_word != '':
            svc = txt.split(src_word)
            return svc[0].strip(), svc[1].strip()
        else: 
            return txt, ''

    def take_loc(txt):
        if re.search('\(.*\)', txt):
            location = re.findall('\((.*)\)', txt)[0]
            non_loc = re.sub(r'\([^)]*\)', '', txt)
        else: 
            location = ''
            non_loc = txt.strip()
        return non_loc.strip(') '), location.strip()

    # split desc into name and serving
    df['name'] = df['desc'].apply(lambda x: take_name(x)[1]).apply(lambda x: take_svc(x)[0])
    df['serving'] = df['desc'].apply(lambda x: take_svc(x)[1]).apply(lambda x: take_name(x)[0])

    # split name into location and name
    df['location'] = df['name'].apply(lambda x: take_loc(x)[1])
    df['name'] = df['name'].apply(lambda x: take_loc(x)[0])

    return df


def combine_continuing_tweets(df):
    """combines tweets for the same elevator outage/fix
    (The continuing tweets have 'That elevator' as an equipment type)

    Parameters
    ----------
    df: pandas.DataFrame 

    Returns
    ----------
    df: pandas.DataFrame
    """

    df['serving_lag'] = df['serving'].shift()
    df['human_eq_type_lag'] = df['human_eq_type'].shift()

    def get_svc_from_lag(row):
        if (row['human_eq_type'] == 'An elevator') & \
            (row['human_eq_type_lag'] == 'That elevator'):
            row['serving'] = row['serving_lag']
        return row
    df = df.apply(get_svc_from_lag, axis = 1)
    df.drop(['serving_lag', 'human_eq_type_lag'], axis = 1, inplace = True)

    # drop the row with 'That elevator'
    df = df[df['human_eq_type'] != 'That elevator']
    df.drop(['desc', 'text'], axis = 1, inplace = True)

    return df

def pair_outage_fix(df):
    df = df.sort_values(['name', 'human_eq_type', 'location', 'serving', 'date'])
    df = df[['name', 'human_eq_type', 'location', 'serving', 'status', 'date']]

    # write a condition to see if they are same equipment as the record after
    grp_cond = ((df.name == df.name.shift(-1)) & \
                (df.human_eq_type == df.human_eq_type.shift(-1)) & \
                (df.location == df.location.shift(-1)) & \
                (df.serving == df.serving.shift(-1)))

    # mark if the record is the same equipment as before
    df['same_equip'] = False
    df.loc[grp_cond, 'same_equip'] = True

    # put the info from 'FIXED' records to the 'FIXED' column of 'OUTAGE' records   
    def get_second_status(row):
        if row['same_equip'] == True: 
            row['status2'] = row['status_lead']
            row['date2'] = row['date_lead']
        return row

    df['date_lead'] = df['date'].shift(-1)
    df['status_lead'] = df['status'].shift(-1)
    df['status2'] = ''
    df['date2'] = ''
    df = df.apply(get_second_status, axis = 1)
    df.drop(['date_lead', 'status_lead', 'same_equip'], axis = 1, inplace = True)

    df['status2_lag'] = df['status2'].shift()
    df = df[(df['status'] != 'FIXED') | (df['status'] != df['status2_lag'])]
    df.drop('status2_lag', axis = 1, inplace = True)

    # write a function to clean out status2 and date2 
    # if they are included in the next record
    def clean_status2(row):
        if row['date_lead'] == row['date2']:
            row['status2'] = ''
            row['date2'] = ''
        return row
    df['date_lead'] = df['date'].shift(-1)
    df = df.apply(clean_status2, axis = 1)
    df.drop('date_lead', axis = 1, inplace = True)

    # if status = 'FIXED', we do not have outage data. drop this.
    df = df[df['status'] != 'FIXED']

    return df