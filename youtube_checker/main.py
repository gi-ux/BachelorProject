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
    # metas = (soup.findAll("meta"))
    # return str(metas[3]).split("'")[1]
    # string = re.search('^*isCrawlable$', content)
    string = content.split('isCrawlable')[0]
    string = string.split('shortDescription')[1]
    return string[3:-3]


def main():

    parser = argparse.ArgumentParser(description='run YouTube checker on ONE file.csv to obtain information on YouTube '
                                                 'Video (such as status, title and description)')
    parser.add_argument('file', type=str,
                        help="This should be the input file with one column named 'URL'.")
    parser.add_argument('--outfilename', type=str, default="output",
                        help="This is the name of .csv file, if not specified is 'output'.")
    args = parser.parse_args()
    urls = list(pd.read_csv(args.file, lineterminator="\n", low_memory=False)["URL"])
    # urls = ["https://www.youtube.com/watch?v=09maaUaRT4M"]
    url, kind, available, reason, title, description = ([] for _ in range(6))
    print(f"Starting parse on {len(urls)} YouTube Videos... ")
    for i in tqdm(urls):
        url.append(i)
        if "https://youtu.be" in i:
            kind.append("compressed")
        else:
            kind.append("decompressed")
        try:
            page = urllib.request.urlopen(i)
            content = page.read()
            content = content.decode('utf-8')
            if "shortDescription" in str(content):
                soup = BeautifulSoup(content, "html.parser")
                title.append(get_title(soup))
                description.append(get_description(content))
                # get_description(str(content))
                # print(str(content))
                available.append(True)
                reason.append("ok")
            else:
                available.append(False)
                title.append(np.nan)
                description.append(np.nan)
                reason.append("This video isn't available anymore")
        except:
            available.append(False)
            r = 'Error 404'
            title.append(np.nan)
            description.append(np.nan)
            reason.append(r)

    df = pd.DataFrame(list(zip(title, description, url, kind, available, reason)),
                      columns=["title", "description", "url", "type", "available", "reason"])
    df.to_csv("data/" + args.outfilename + ".csv", index=False, line_terminator="\n", encoding="utf-8")
    print("Parsing done!")

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(df)


if __name__ == '__main__':
    main()
