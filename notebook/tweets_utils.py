import datetime
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait as futures_wait
import numpy as np
import pandas as pd
import tqdm
import matplotlib.pyplot as plt
import plotly.express as px

logger = logging.getLogger("main")
workers = 7
chunksize = int(1e6)

    ########################### process data tweets ###########################

def process_data_tweets(df: pd.DataFrame, list_users):
#     original = df[df['rt_created_at'].isna() & df['in_reply_to_status_id'].isna()]
#     retweet = df[df['rt_created_at'].notna()]
#     reply = df[df['in_reply_to_status_id'].notna()]
#     tweet_creation = []
#     for x in df['created_at']:
#         data = (str(x))
#         formatted = process_datetime(data)
#         tweet_creation.append(datetime.datetime.strptime(formatted, '%d-%m-%Y'))
    df = df[df.user_screen_name.isin([x for x in list_users])]
    return {
#             "ids": df["user_id"], 
            "users": df["user_screen_name"],
#             "hashtags":df["hashtags"],
#             "urls":df["urls"],
#             "text":df["text"],
#             "original_ids": original["user_id"], 
#             "original_users": original["user_screen_name"], 
#             "reply_ids": reply['user_id'], 
#             "reply_users": reply['user_screen_name'],
#             "replied_ids": reply['in_reply_to_user_id'], 
#             "replied_users": reply['in_reply_to_screen_name'],
#             "retweet_ids": retweet["user_id"], 
#             "retweet_users": retweet["user_screen_name"],
#             "retweeted_ids": retweet['rt_user_id'], 
#             "retweeted_users": retweet['rt_user_screen_name'],
#             "total_len" :len(df), 
#             "original_len": len(original), 
#             "retweet_len": len(retweet), 
#             "reply_len": len(reply)
#             "created_at": df["created_at"]
    }

def process_data_users(df: pd.DataFrame):
    return {
            'users': df['screen_name'], 
            'ids': df['id'],
            'verified': df["verified"]
            }

def process_data_verified(df: pd.DataFrame, list_users):
    df = df[df.user_screen_name.isin([x for x in list_users])]
    return {'df': df}


def process_data_verified_profiles(df: pd.DataFrame, list_users):
    df = df[df.screen_name.isin([x for x in list_users])]
    return {'df': df}


def process_data_hashtags(df: pd.DataFrame):        
    return {
        'name': df["user_screen_name"],
        'hashtags':df["hashtags"]
           }

def process_data_disinformation(df: pd.DataFrame, lista):
    original = df[df['rt_created_at'].isna() & df['in_reply_to_status_id'].isna()]
    retweet = df[df['rt_created_at'].notna()]
    reply = df[df['in_reply_to_status_id'].notna()]
    original = original.reset_index(drop=True)
    retweet = retweet.reset_index(drop=True)
    reply = reply.reset_index(drop=True)
    
    id_tweet_original = [] 
    hashtag_original = []
    original_tweet = []
    original_id = []
    link = []
    
    id_tweet_rt = [] 
    hashtag_rt = []
    
    id_tweet_rp = [] 
    hashtag_rp = []
    
    disinform_rt_name = []
    disinform_rt_id = []
    rt_name = []
    rt_id = []
    link_tweet = []
    
    disinform_replied_name = []
    disinform_replied_id = []
    rp_name = []
    rp_id = []
    link_rp = []
    
    res = 0
    d_total_len = 0
    d_original_len = 0
    d_retweet_len = 0
    d_reply_len = 0
    
    for i in original["user_screen_name"]:
        if(found(i,lista)):
            d_total_len = d_total_len + 1
            d_original_len = d_original_len + 1
            val = list(original["user_screen_name"]).index(i,res)
            original_tweet.append(i)
            original_id.append(original["user_id"][val])
            link.append(original["urls"][val])
            id_tweet_original.append(original["id"][val])
            hashtag_original.append(original["hashtags"][val])
            res = val + 1
            
    res = 0
    for i in retweet["rt_user_screen_name"]:
        if(found(i,lista)):
            d_total_len = d_total_len + 1
            d_retweet_len = d_retweet_len + 1
            val = list(retweet["rt_user_screen_name"]).index(i,res)
            disinform_rt_name.append(i)
            disinform_rt_id.append(retweet["rt_user_id"][val])
            rt_id.append(retweet["user_id"][val])
            rt_name.append(retweet["user_screen_name"][val])
            link_tweet.append(retweet['urls'][val])
            id_tweet_rt.append(retweet["id"][val])
            hashtag_rt.append(retweet["hashtags"][val])
            res = val + 1
    res = 0
    for i in retweet["user_screen_name"]:
        if(found(i,lista)):
            d_total_len = d_total_len + 1
            d_retweet_len = d_retweet_len + 1
            val = list(retweet["user_screen_name"]).index(i,res)
            disinform_rt_name.append(i)
            disinform_rt_id.append(retweet["rt_user_id"][val])
            rt_id.append(retweet["user_id"][val])
            rt_name.append(retweet["user_screen_name"][val])
            link_tweet.append(retweet['urls'][val])
            id_tweet_rt.append(retweet["id"][val])
            hashtag_rt.append(retweet["hashtags"][val])
            res = val + 1
    res = 0
    for i in reply['in_reply_to_screen_name']:
        if(found(i,lista)):
            d_total_len = d_total_len + 1
            d_reply_len = d_reply_len + 1
            val = list(reply['in_reply_to_screen_name']).index(i,res)
            disinform_replied_name.append(i)
            disinform_replied_id.append(reply['in_reply_to_user_id'][val])
            rp_name.append(reply['user_screen_name'][val])
            link_rp.append(retweet['urls'][val])

            rp_id.append(reply["user_id"][val])
            id_tweet_rp.append(reply["id"][val])
            hashtag_rp.append(reply["hashtags"][val])
            res = val + 1
    return {
        #original
        'id_original':id_tweet_original,
        'hashtag_original':hashtag_original,
        "original_names":original_tweet,
        'original_ids': original_id,
        'links': link,        
        #retweet
        "id_rt": id_tweet_rt,
        "hashtag_rt": hashtag_rt,
        "retweet_ids": rt_id, 
        "retweet_users": rt_name,
        "retweeted_ids": disinform_rt_id, 
        "retweeted_users": disinform_rt_name,
        "rt_link" : link_tweet,
        #reply
        "id_rp": id_tweet_rp,
        "hashtag_rp": hashtag_rp,
        "reply_ids": rp_id, 
        "reply_users": rp_name,
        "link_rp": link_rp,
        "replied_ids": disinform_replied_id, 
        "replied_users": disinform_replied_name,
        #length
        "total_len" :len(df), 
        "original_len": len(original), 
        "retweet_len": len(retweet), 
        "reply_len": len(reply),
        "d_total_len" :d_total_len, 
        "d_original_len": d_original_len, 
        "d_retweet_len": d_retweet_len, 
        "d_reply_len": d_reply_len
    }

def process_bots(df: pd.DataFrame, lista):
    lista = list(lista)
    df_user = df[df["user_screen_name"].isin(x for x in lista)]
    df_rt = df[df["rt_user_screen_name"].isin(x for x in lista)]
    original = df[df['rt_created_at'].isna() & df['in_reply_to_status_id'].isna()]
    retweet = df[df['rt_created_at'].notna()]
    reply = df[df['in_reply_to_status_id'].notna()]
    return {
        'df': df_user,
        'df_rt': df_rt,
        'len_total':len(df),
        'len_original':len(original),
        'len_retweet':len(retweet),
        'len_reply':len(reply)
        }

def process_all_data(filename, cols, flag, list_name=None, chunksize=chunksize, workers=workers):
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
#                     futures.append(executor.submit(process_data_tweets, sc, list_name))
#                     futures.append(executor.submit(process_data_disinformation, sc, list_name))
#                     futures.append(executor.submit(process_data_hashtags, sc))
#                     futures.append(executor.submit(process_bots, sc, list_name))
                    futures.append(executor.submit(process_data_verified, sc, list_name))

                else:
#                     futures.append(executor.submit(process_data_users, sc))
                    futures.append(executor.submit(process_data_verified_profiles, sc, list_name))


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

 ############################## Utils ##############################  

def hashtag_normalize(i):
    hashtag = []
    if(i != "[]" ) and (not type(i) == float):
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

def hashtag_process_list(list_hashtag):
    hashtag = []
    for i in list_hashtag:
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
    
def print_pie_chart3(title, name1, name2, name3, len1, len2, len3):
    label = [name1, name2, name3]
    data = [len1, len2, len3]
    explode = (0.1, 0.1, 0.1)

    # Creating color parameters
    colors = ( "lightgreen", "orange", "cyan")

    # Wedge properties
    wp = { 'linewidth' : 1, 'edgecolor' : "black" }

    # Creating autocpt arguments
    def func(pct, allvalues):
        absolute = int(pct / 100.*np.sum(allvalues))
        return "{:.1f}%\n({:d})".format(pct, absolute)

    # Creating plot
    fig, ax = plt.subplots(figsize =(10, 7))
    wedges, texts, autotexts = ax.pie(data, 
                                      autopct = lambda pct: func(pct, data),
                                      explode = explode, 
                                      labels = label,
                                      shadow = True,
                                      colors = colors,
                                      startangle = 90,
                                      wedgeprops = wp)

    # Adding legend
    ax.legend(wedges, label,
              title ="Legend",
              loc ="center left",
              bbox_to_anchor =(1, 0, 0.5, 1))

    plt.setp(autotexts, size = 8, weight ="bold")
    ax.set_title(title)
    plt.show()
    
def stats(total_len, original_len, retweet_len, reply_len):
    print(f'Number of total tweets: {total_len}')
    print(f'Number of original tweets: {original_len}')
    print(f'Number of retweet: {retweet_len}')
    print(f'Number of reply: {reply_len}')

    perc_original = np.around(original_len*100/total_len,2)
    perc_retweet = np.around(retweet_len*100/total_len,2)
    perc_reply = np.around(reply_len*100/total_len,2)
    print(f'Number of original_tweets: {perc_original}% of total tweets')
    print(f'Number of retweets: {perc_retweet}% of total tweets')
    print(f'Number of replies: {perc_reply}% of total tweets')

    print('Check sum == len(tweets): ',original_len + retweet_len + reply_len == total_len)
    
    
    
def check_credibility(list_url, df):
    list_credibility = []
    for i in list_url:
        for j in range(len(df["Domain"])):
            if(i == df["Domain"][j]):
                list_credibility.append((i,df["Class"][j]))
    class_domain = []
    for i in range(len(list_credibility)):
        class_domain.append(list_credibility[i][1])
    class_domain = pd.Series(class_domain).value_counts().sort_values()
    labels = [class_domain.keys()[0], class_domain.keys()[1]]
    values = [class_domain.high, class_domain.low]
    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    plt.show()
    return list_credibility
    
    
def remove_www(url_list):
    urls_rt_beauty = []
    for i in url_list:
        value = i
        if value is None:
            continue
        elif "www" in i:
            splitted = i.split(".")
            if(len(splitted) > 2):
                value = splitted[1] + "." + splitted[2]
            else:
                value = splitted[1]
        urls_rt_beauty.append(value)
    return urls_rt_beauty


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
    data = str(datetime.datetime.strptime(formatted_data, '%d-%m-%Y')).split()[0]
    return data

def found(name, list_name):
    for i in list_name:
        if(name.lower() == i.lower()):
            return True
    return False

def url_decompress(url):
    if isinstance(url, float) == False:
        x = url.split()
        url = x[3].translate({ord("'"): None})
        url = url.split("//")
        url = url[1].split("/")
        return url[0]

    
def format_urls(urls):
    urls = [url_decompress(v) if v != "[]" else "0" for v in urls]
    urls = list(filter(lambda num: num != "0", urls))
    urls = remove_www(urls)
    return urls


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