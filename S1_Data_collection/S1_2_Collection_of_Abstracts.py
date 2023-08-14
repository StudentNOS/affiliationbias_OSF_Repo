
from paperscraper.get_dumps import medrxiv

# load medrxiv metadata once
# copy metadata file 'medrxiv_2023-05-14.jsonl' to local repo 
# (otherwise it gets overwritten next time the script is run)
#medrxiv()

from paperscraper.xrxiv.xrxiv_query import XRXivQuery
from paperscraper.utils import load_jsonl


import json
import pandas as pd


# load and clean jsonl file----------------------------------------------------
# read jsonl file as dataframe
df = pd.read_json('medrxiv_scraping/medrxiv_2023-06-16.jsonl', lines=True)

# convert date column to datetime
df['date'] = pd.to_datetime(df['date'])

# sort by date column, newest first
df = df.sort_values(by='date', ascending=False)
df['date_str'] = df['date'].dt.strftime('%Y/%m/%d')


# selecting the last 30 papers from stack ---------------------------------
# only keep papers from 2023
df30 = df[0:30]

# save as csv
df30.to_csv('medrxiv_scraping/medrxiv_last30_23_06_16.csv', sep = ';', index=False)
