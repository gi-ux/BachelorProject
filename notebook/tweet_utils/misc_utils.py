import datetime
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait as futures_wait
import numpy as np
import pandas as pd
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import json
import urllib.request

# Read data from Json file
def read_from_json(path):
    start_time = time.perf_counter()
    file = open (path,)
    obj = json.loads(file.read())
    file.close()
    stop_time = time.perf_counter()
    print("Time: ",stop_time-start_time)
    return obj

# Split DF
def split_df(df: pd.DataFrame):
    ### Original tweets
    original = df[df["in_reply_to_screen_name"].isna() & df["rt_created_at"].isna() & df["quoted_status_id"].isna()]
    nan_value = float("NaN")
    original_w_mentions = original.replace("[]", nan_value)
    original_w_mentions = original_w_mentions[original_w_mentions["user_mentions"].notna()]

    ### Replies
    reply = df[df["in_reply_to_user_id"].notna() & df["quoted_status_id"].isna()]
    mentions = reply[reply["in_reply_to_status_id"].isna()]
    original = original.append(mentions)
    original_w_mentions = original_w_mentions.append(mentions)
    reply = reply.drop(mentions.index)
    reply_to_status = reply[reply["in_reply_to_status_id"].notna()]

    ### Retweets
    retweet = df[df["rt_created_at"].notna()]
    retweet_original = retweet[retweet["rt_in_reply_to_user_id"].isna() & retweet["quoted_status_id"].isna()]
    retweet_in_reply = retweet[retweet["rt_in_reply_to_status_id"].notna()]
    retweet_of_mentions = retweet[
        retweet["rt_in_reply_to_status_id"].isna() & retweet["rt_in_reply_to_user_id"].notna()]

    ### Quotes
    quote = df[df["quoted_status_id"].notna() & df["rt_created_at"].isna()]
    quote_original = quote[quote["in_reply_to_screen_name"].isna()]
    quote_reply = quote[quote["in_reply_to_screen_name"].notna() & quote["in_reply_to_status_id_str"].notna()]
    quote_mention = quote[quote["in_reply_to_status_id"].isna() & quote["in_reply_to_user_id"].notna()]

    return {
        'original': original,
        'original_mention': original_w_mentions,
        'reply': reply,
        'reply_to_status': reply_to_status,
        'retweet': retweet,
        'rt_original': retweet_original,
        'rt_in_reply': retweet_in_reply,
        'rt_mention': retweet_of_mentions,
        'quote': quote,
        'quote_original': quote_original,
        'quote_reply': quote_reply,
        'quote_mention': quote_mention
    }

# If DF contains dirty char run df = clean_data_format(df)
def clean_data_format(df: pd.DataFrame, fix_encoding=False, broken_col='text'):
    col = df.columns[-1]

    def clean(target):
        return str(target).replace("\r", "")

    if "\r" in col:
        clean_col = clean(col)
        df = df.rename(columns={col: clean_col})
        if df[clean_col].dtype.name == 'object':
            df[clean_col] = df[clean_col].apply(clean)
    if fix_encoding:
        df[broken_col] = df[broken_col].apply(util.fix_encoding)
    return df

# Obtain list of hashtags from DF
def hashtag_process(df):
    hashtag = []
    for i in df["hashtags"]:
        if(i != "[]") and (not type(i) == float):
            x = i.split(" ")
            length = (len(x)) // 5
            index = 0
            for j in range(length):
                index = index + 1
                val = x[index].replace("'", "")
                x_replace = val.replace(",", "")
                hashtag.append(x_replace)
                index = index + 4
    return hashtag