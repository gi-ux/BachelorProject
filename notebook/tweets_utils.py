import datetime
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait as futures_wait
import numpy as np
import pandas as pd
import tqdm
logger = logging.getLogger("main")
workers = 7
chunksize = int(1e6)


def process_datetime(data):
    if ((data == "nan") or (data == "False") or (data == "None")):
        month = "01"
        day = "01"
        year = "2006"
    else:
        x = data.split()
        month = str(time.strptime(x[1], '%b').tm_mon)
        day = str(x[2])
        year = str(x[5])
    formatted_data = day + "-" + month + "-" + year
    return formatted_data

def process_data_tweets(df: pd.DataFrame):
    original = df[df['rt_created_at'].isna() & df['in_reply_to_status_id'].isna()]
    retweet = df[df['rt_created_at'].notna()]
    reply = df[df['in_reply_to_status_id'].notna()]
#     tweet_creation = []
#     for x in df['created_at']:
#         data = (str(x))
#         formatted = process_datetime(data)
#         tweet_creation.append(datetime.datetime.strptime(formatted, '%d-%m-%Y'))
    return {
#             "ids": df["user_id"], 
#             "users": df["user_screen_name"],
            "original_ids": original["user_id"], 
            "original_users": original["user_screen_name"], 
            "reply_ids": reply['user_id'], 
            "reply_users": reply['user_screen_name'],
            "replied_ids": reply['in_reply_to_user_id'], 
            "replied_users": reply['in_reply_to_screen_name'],
            "retweet_ids": retweet["user_id"], 
            "retweet_users": retweet["user_screen_name"],
            "retweeted_ids": retweet['rt_user_id'], 
            "retweeted_users": retweet['rt_user_screen_name'],
            "total_len" :len(df), 
            "original_len": len(original), 
            "retweet_len": len(retweet), 
            "reply_len": len(reply)
#             "creation": tweet_creation
    }

def process_data_users(df: pd.DataFrame):
    return {
            'users': df['screen_name'], 
            'ids': df['id'],
            'verified': df["verified"]
            }

def found(name, list_name):
    for i in list_name:
        if(name == i):
            return True
    return False

def process_data_disinformation(df: pd.DataFrame, lista):
    return {
        'user': df["user_screen_name"], 
        'content': df["text"]
    }

def process_all_data(filename, cols, flag, list_name, chunksize=chunksize, workers=workers):
    c = 1
    executor = ProcessPoolExecutor(max_workers=workers)
    futures = []
    partial_results = []
    results = []
    chunks = pd.read_csv(filename, lineterminator='\n', chunksize=chunksize, usecols=cols, low_memory=False)
    chunk = None
    try:
        chunk = next(chunks)
    except StopIteration:
        chunk = None
    i = 0
    while chunk is not None:
        print(f"Processing chunk {c}")
        subchunks = np.array_split(chunk, workers)
        for sc in subchunks:
            try:
                if (flag == True):
#                     futures.append(executor.submit(process_data_tweets, sc))
                    futures.append(executor.submit(process_data_disinformation, sc, list_name))
                else:
                    futures.append(executor.submit(process_data_users, sc))

            except Exception as e:
                logger.exception("Error", e)
            i += 1
        try:
            chunk = next(chunks)
        except StopIteration:
            chunk = None
        c += 1
        futures_wait(futures)
        try:
            partial_results = [fut.result() for fut in futures]
        except Exception as e:
            logger.exception("Error", e)
    results.append(partial_results)
    return results

############################## Processed Data ##############################  

def search_in_df(df: pd.DataFrame, user):
    found = df[df['id'].astype(str).str.contains(user)]
    return found.count()

def process_bots(df: pd.DataFrame, bots):
    for i in bots():
        found = search_in_df(i[0])
        if found[0] > 0:
            print("funzione che mi ritorna le info per quell'id")
            #funzione che mi ritorna le info per quell'id