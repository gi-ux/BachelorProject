import urllib.request
import numpy as np
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup
import argparse

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


def main():
    parser = argparse.ArgumentParser(description='run YouTube checker on ONE file.csv to obtain information on YouTube '
                                                 'Video (such as status, title and description)')

    parser.add_argument('file', type=str,
                        help="This should be the input file with one column named 'user_screen_name' and 'urls.")

    parser.add_argument('--outfilename', type=str, default="data/output.csv",
                        help="This is the name of .csv file, if not specified is 'output'.")
    args = parser.parse_args()
    df_parsed = clean_url(pd.read_csv(args.file, lineterminator="\n", low_memory=False, encoding="utf-8"))
    urls = list(df_parsed["link"])
    name = list(df_parsed["user_screen_name"])
    kind, available, reason, title, description = ([] for _ in range(5))

    print(f"Starting parse on {len(urls)} YouTube Videos... ")
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

    df = pd.DataFrame(list(zip(name, title, description, urls, kind, available, reason)),
                      columns=["screen_name", "title", "description", "url", "type", "available", "reason"])
    df.to_csv(args.outfilename, index=False, line_terminator="\n", encoding="utf-8")
    print("Parsing done!")


if __name__ == '__main__':
    main()
