import urllib.request
import numpy as np
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup
import argparse


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
                        help="This should be the input file with one column named 'URL' and 'NAME.")
    parser.add_argument('--outfilename', type=str, default="data/output.csv",
                        help="This is the name of .csv file, if not specified is 'output'.")
    args = parser.parse_args()
    urls = list(pd.read_csv(args.file, lineterminator="\n", low_memory=False)["URL"])
    # urls = ["https://www.youtube.com/watch?v=09maaUaRT4M", "https://www.youtube.com/WHO",
    # "https://www.youtube.com/playlist?list=PLiC5xPi..."]
    kind, available, reason, title, description = ([] for _ in range(5))
    names = list(pd.read_csv(args.file, lineterminator="\n", low_memory=False)["NAME"])
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

    df = pd.DataFrame(list(zip(names, title, description, urls, kind, available, reason)),
                      columns=["user_name", "title", "description", "url", "type", "available", "reason"])
    df.to_csv(args.outfilename, index=False, line_terminator="\n", encoding="utf-8")
    print("Parsing done!")
    # df = pd.DataFrame(list(zip( title, description, urls, kind, available, reason)), columns=["title",
    # "description", "url", "type", "available", "reason"]) with pd.option_context('display.max_rows', None,
    # 'display.max_columns', None):  # more options can be specified also print(df)


if __name__ == '__main__':
    main()
