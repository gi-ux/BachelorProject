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


logger = logging.getLogger("main")
workers = 7
chunksize = int(1e6)

    ########################### process data tweets ###########################
def process_quotes(df: pd.DataFrame):
#     original = df[df['rt_created_at'].isna() & df['in_reply_to_status_id'].isna() & df['quoted_status_created_at'].isna()]
#     quotes = df[df['quoted_status_created_at'].isna()]
    retweet = df[df['rt_created_at'].notna()]
    retweet_checksum = len(retweet[retweet["quoted_status_created_at"].notna()])
#     reply = df[df['in_reply_to_status_id'].notna()]
    return {
            "rt_len" : len(retweet),
            "quotes_rt_len" : retweet_checksum
    }
    
    
def process_data_tweets(df: pd.DataFrame):
    df = df[df["text"].notna()]
    return {
        "text":df["text"]
    }


def process_data_rt(df: pd.DataFrame, list_users):
    df = df[df["rt_created_at"].notna()]
    df = df[df.rt_user_screen_name.isin([x for x in list_users])]
    return {
        'user': df["user_screen_name"]
           }


def process_data_verified_profiles(df: pd.DataFrame):
    return {'df': df}


def process_data_hashtags(df: pd.DataFrame):        
    return {
        'name': df["user_screen_name"],
        'hashtags':df["hashtags"]
           }


def process_data_get_names(df: pd.DataFrame):
    return {"df": df}


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
                    futures.append(executor.submit(process_data_rt, sc, list_name))

                else:
#                     futures.append(executor.submit(process_data_users, sc))
                    futures.append(executor.submit(process_data_verified_profiles, sc))


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
def plot_distribution(df: pd.DataFrame, title, column_name, xmin=0, xmax=1):
    index = [10, 90]
    box = list(df[column_name])
    perc_numpy = [np.percentile(box, i, interpolation='nearest') for i in index]
    # # Plotting
    plt.hist(box, 50)
    for i in range(len(index)):
        plt.axvline(perc_numpy[i], color='r')
    plt.title(title)
    plt.xlim(xmin=xmin, xmax=xmax)
    plt.show()
    
    
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
   
    
def print_pie_chart4(title, name1, name2, name3, name4, len1, len2, len3, len4):
    label = [name1, name2, name3, name4]
    data = [len1, len2, len3, len4]
    explode = (0.1, 0.1, 0.1, 0.1)

    # Creating color parameters
    colors = ( "lightgreen", "orange", "cyan", "grey")

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
    
    
def stats(total_len, original_len, retweet_len, reply_len, quote_len):
    print(f'Number of total tweets: {total_len}')
    print(f'Number of original tweets: {original_len}')
    print(f'Number of retweets: {retweet_len}')
    print(f'Number of replies: {reply_len}')
    print(f'Number of quotes: {quote_len}')

    perc_original = np.around(original_len*100/total_len,2)
    perc_retweet = np.around(retweet_len*100/total_len,2)
    perc_reply = np.around(reply_len*100/total_len,2)
    perc_quote = np.around(quote_len*100/total_len,2)
    print(f'Number of original_tweets: {perc_original}% of total tweets')
    print(f'Number of retweets: {perc_retweet}% of total tweets')
    print(f'Number of replies: {perc_reply}% of total tweets')
    print(f'Number of quotes: {perc_quote}% of total tweets')

    print('Check sum == len(tweets): ',original_len + retweet_len + reply_len + quote_len == total_len)
    
    
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
#         x = url.split()
#         url = x[3].translate({ord("'"): None})
#         url = check_compression(url, df)
        url = url.split("//")
        if (url[0] is None) | (url[0] == "None") | (url[0] == '/') | ("http" not in url[0]):
            print("invalid data")
        else:
#             print(url)
            url = url[1].split("/")
            return url[0]

        
def substitute_compressed_url(df, expanded_urls):
    df_urls = df.loc[df['urls'] != '[]']
    df_urls["urls"] = [x.split()[3].translate({ord("'"): None}).replace(",","") for x in df_urls["urls"]]
    df_merge = df_urls.merge(expanded_urls, how="left", left_on="urls", right_on="url")
    x = df_merge[df_merge["url"].notna()]
    for index, row in x.iterrows():
        df_urls.loc[df_urls["urls"]==row["url"], "urls"] = row["expanded"]
    print("Beautify...")
    urls = df_urls["urls"]
    urls = [tweets_utils.url_decompress(v) for v in urls]
    urls = tweets_utils.remove_www(urls)
    return urls  
    

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


def print_perc(value_1, value_2):
    return (round(value_1/value_2,2)*100)


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
    retweet_of_mentions = retweet[retweet["rt_in_reply_to_status_id"].isna() & retweet["rt_in_reply_to_user_id"].notna()]
    
    ### Quotes
    quote = df[df["quoted_status_id"].notna() & df["rt_created_at"].isna()]
    quote_original = quote[quote["in_reply_to_screen_name"].isna()]
    quote_reply = quote[quote["in_reply_to_screen_name"].notna() & quote["in_reply_to_status_id_str"].notna()]
    quote_mention = quote[quote["in_reply_to_status_id"].isna() & quote["in_reply_to_user_id"].notna()] 
 
    return {
        'original':original,
        'original_mention':original_w_mentions,
        'reply':reply,
        'reply_to_status':reply_to_status,
        'retweet':retweet,
        'rt_original':retweet_original,
        'rt_in_reply':retweet_in_reply,
        'rt_mention':retweet_of_mentions,
        'quote':quote,
        'quote_original':quote_original,
        'quote_reply':quote_reply,
        'quote_mention':quote_mention
    }


def plt_hist(name1, name2, value1, value2, labels, xaxis, yaxis, title):
    fig = go.Figure()
    fig.add_trace(go.Histogram(histfunc="sum", y=value1, x=labels, name=name1))
    fig.add_trace(go.Histogram(histfunc="sum", y=value2, x=labels, name=name2))
    fig.update_layout(
        title=title,
        xaxis_title=xaxis,
        yaxis_title=yaxis,
        legend_title="Legend")
    fig.show()
    
    
def read_from_json(path):
    start_time = time.perf_counter()
    file = open (path, encoding = "utf-8")
    obj = json.loads(file.read())
    file.close()
    stop_time = time.perf_counter()
    print("Time: ",stop_time-start_time)
    return obj

def plot_two_hist(s1: pd.Series, s2: pd.Series, name):
    good_lst_val = list(s1.values)
    good_lst_com = list(s1.keys())
    good_lst = []
    [good_lst.append("good") for i in good_lst_com]
    bad_lst_val = list(s2.values)
    bad_lst_com = list(s2.keys())
    bad_lst = []
    [bad_lst.append("bad") for i in bad_lst_com]
    df_plot = pd.DataFrame(list(zip(good_lst_val, good_lst_com, good_lst)), 
                           columns=["Val", "Community", "Dozen"])
    df_plot = df_plot.append(pd.DataFrame(list(zip(bad_lst_val, bad_lst_com, bad_lst)), 
                           columns=["Val", "Community", "Dozen"]))
    df_plot = df_plot.sort_values(by="Val", ascending=False)
    df_plot["Community"] = df_plot["Community"].astype(str)
    fig = px.bar(df_plot, x="Val", y="Community", color="Dozen", barmode='group', 
                 title=name, orientation="h",  color_discrete_map={
        'good': 'blue',
        'bd': 'green'})
    fig.update_layout(
    font_size = 18,
    yaxis = dict(autorange="reversed")
    )
    fig.show()

def check_availability(urls):
    url = []
    kind = []
    available = []
    reason = []
    for i in tqdm(urls):
        url.append(i)
        if "https://youtu.be" in i:
            kind.append("compressed")
        else:
            kind.append("decompressed")
        try:
            page = urllib.request.urlopen(i)
            content = page.read()
            if "shortDescription" in str(content):
                available.append(True)
                reason.append("ok")
            else:
                available.append(False)
                reason.append("This video isn't available anymore")
        except:
            available.append(False)
            r = 'Error 404'
            reason.append(r)
    return pd.DataFrame(list(zip(url, kind, available, reason)), 
                        columns=["url", "type", "available", "reason"])