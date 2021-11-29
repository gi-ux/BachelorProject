import pandas as pd
import glob
import re
from tqdm import tqdm
from nltk.corpus import stopwords
import argparse

path_names = glob.glob("C:/Users/gianl/Desktop/Gi/Supsi/BachelorProject/csv/")[0]
cachedStopWords = stopwords.words("english")
custom_words = list(pd.read_csv(path_names + "words_to_remove.csv",
                                lineterminator="\n", low_memory=False)["word"])


def clean_cached(text):
    text = ' '.join([word for word in text.split() if word not in cachedStopWords])
    text = ' '.join([word for word in text.split() if word not in custom_words])
    return text


def write_file_text(df: pd.DataFrame, name: str, col_name: str):
    text_file = open(f"{name}.txt", "w", encoding="utf-8")
    # for i in df["text"]:
    for i in tqdm(df[col_name]):
        content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', str(i))
        content = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|[^a-zA-Z0-9\s]",
                                  " ", content).split())
        content = content.lower()
        content = clean_cached(content)
        text_file.write(content + "\n")
    text_file.close()


def write_file_hashtag(df: pd.DataFrame, name: str, col_name: str):
    text_file = open(f"{name}.txt", "w", encoding="utf-8")
    hashtag = []
    for i in tqdm(df[col_name]):
        hashtag.extend(re.findall(r'\B#\w*[a-zA-Z]+\w*', i))

    for i in hashtag:
        text_file.write(i + "\n")
    text_file.close()


def main():
    parser = argparse.ArgumentParser(description='run text_wrapper to clean DF field and turn it into .txt file')
    parser.add_argument('input_filename', type=str,
                        help="This should be the input file.")
    parser.add_argument('--output_filename', type=str, default="input",
                        help="This is the name of .txt file, if not specified is 'output'.")
    parser.add_argument('--col_name', type=str, default="text",
                        help="This is the name of column picked for data parsing, if not specified is 'text'.")
    parser.add_argument('--hashtags', type=bool, default=False,
                        help="This is a flag for scanning hashtags.")
    args = parser.parse_args()
    filenames = sorted(glob.glob(args.input_filename))
    files = [name for name in filenames]
    if len(files) != 1:
        print("You only need to pass ONE file and output filename.")
    else:
        cols = [args.col_name]
        print("Start processing...")
        print("Reading input file...")
        df = pd.read_csv(args.input_filename, lineterminator="\n", low_memory=False, usecols=cols)
        df = df[df[args.col_name].notna()]
        print("Done!")
        print("Cleaning input file...")
        if not args.hashtags:
            print("Writing text file...")
            write_file_text(df, "data/" + args.output_filename, args.col_name)
        else:
            print("Writing hashtag file...")
            write_file_hashtag(df, "data/" + args.output_filename, args.col_name)

        print("Done!")

    # lst = ["rashid", "kellybroganmd", "buttar", "drtedros", "ashishkjha", "unhealthytruth", "brogan", "mercola",
    #        "drmikeryan", "edyong209", "mlipsitch", "helenbranswell"]
    # df = pd.DataFrame(lst, columns=["word"])
    # df.to_csv(path_names + "words_to_remove.csv", index=False, encoding="utf-8", line_terminator="\n")


if __name__ == '__main__':
    main()
