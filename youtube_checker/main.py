import urllib.request
import numpy as np
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import wait as futures_wait
from concurrent.futures.process import ProcessPoolExecutor
import argparse
import glob

def clean_url(df):
    yt_df = df[(df["urls"].str.contains("https://youtu.be")) | (df["urls"].str.contains("https://youtube"))]
    screen_name = []
    lst_urls = []
    for row in tqdm(yt_df.itertuples()):
        url_exp = row.urls.split(" ")
        for exp in range(len(url_exp)):
            if url_exp[exp] == "'expanded_url':":
                lst_urls.append(url_exp[exp + 1][1:-2])
                screen_name.append(row.user_screen_name)
    return pd.DataFrame(list(zip(screen_name, lst_urls)), columns=["user_screen_name", "link"])

def get_title(soup):
    metas = (soup.findAll("meta"))
    return str(metas[2]).split('"')[1]


def get_description(content):
    string = content.split('isCrawlable')[0]
    string = string.split('shortDescription')[1]
    return string[3:-3]

def get_from_args():
    parser = argparse.ArgumentParser(description='run YouTube checker on ONE file.csv to obtain information on YouTube '
                                                 'Video (such as status, title and description)')

    parser.add_argument('file', type=str,
                        help="This should be the input file with one column named 'user_screen_name' and 'urls.")

    parser.add_argument('--outfilename', type=str, default="data/output.csv",
                        help="This is the name of .csv file, if not specified is 'output'.")
    args = parser.parse_args()
    df_parsed = clean_url(pd.read_csv(args.file, lineterminator="\n", low_memory=False, encoding="utf-8"))
    return df_parsed

def parse_yt_parallel(urls: list):
    # results = pd.DataFrame()
    futures = []
    executor = ProcessPoolExecutor(max_workers=8)
    sublist = np.array_split(urls, 8)
    count = 0
    for sc in sublist:
        futures.append(executor.submit(scrape, sc, count))
        count = count + 1
    futures_wait(futures)
    # for fut in futures:
    #     results = results.append(fut.result())
    # results.reset_index(drop=True, inplace=True)
    # return results

# def scrape(urls: list, count: int):
#     print(f"Worker {count} parsing on {len(urls)} YouTube Videos... ")
#     return pd.DataFrame(list(urls), columns=["Len"])

def scrape(urls: list, count: int):
    kind, available, reason, title, description = ([] for _ in range(5))
    print(f"Worker {count} parsing on {len(urls)} YouTube Videos... ")
    for i in tqdm(urls):
        if "https://youtu.be" in i:
            kind.append("compressed")
        else:
            kind.append("decompressed")
        try:
            page = urllib.request.urlopen(i)
            content = page.read()
            content = content.decode('utf-8')
            content = str(content)
            if "shortDescription" in content:
                soup = BeautifulSoup(content, "html.parser")
                title.append(get_title(soup))
                description.append(get_description(content))
                available.append(True)
                reason.append("Parsed")
            elif "www.youtube.com/playlist?list=" in i:
                title.append(np.nan)
                description.append(np.nan)
                available.append(True)
                reason.append("Playlist")
            elif 'content="profile"' in content:
                available.append(True)
                title.append(np.nan)
                description.append(np.nan)
                reason.append("Profile")
            else:
                available.append(False)
                title.append(np.nan)
                description.append(np.nan)
                reason.append("Unavailable")
        except:
            available.append(False)
            title.append(np.nan)
            description.append(np.nan)
            reason.append('Error 404')
    df = pd.DataFrame(list(zip(title, description, urls, kind, available, reason)),
                      columns=["title", "description", "url", "type", "available", "reason"])
    print(f"Worker {count} finished!")
    df.to_csv(f"./data/worker{count}.csv", line_terminator="\n", encoding="utf-8", index=False)
    print(f"Worker {count} wrote file!")


def main():
    urls = pd.read_csv("./data/youtube_russiaukraine.csv", lineterminator="\n", encoding="utf-8", low_memory=False)["URL"]
    parse_yt_parallel(urls)
    print("Completed parsing")


if __name__ == '__main__':
    # main()
    path_data = glob.glob("./data/worker*.csv")
    df = pd.DataFrame()
    for path in path_data:
        df = df.append(pd.read_csv(path))
    df.to_csv("./data/url_parsed.csv", encoding="utf-8", index=False, line_terminator="\n")