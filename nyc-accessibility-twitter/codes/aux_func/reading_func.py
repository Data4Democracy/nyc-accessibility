import datadotworld as dw

def read_tweets():
    lds = dw.load_dataset('bkey/nycoutages-tweets')
    return lds.dataframes['nyc_outages_tweets'] 
    
