import pandas as pd
import glob
import re
from nltk.corpus import stopwords
import runSage

path = glob.glob("C:/Users/gianl/Desktop/Gi/Supsi/BachelorProject/large_files/ccdh/")[0]
path_names = glob.glob("C:/Users/gianl/Desktop/Gi/Supsi/BachelorProject/csv/")[0]
cachedStopWords = stopwords.words("english")
good = pd.read_csv(path_names + "all_good_users.csv", lineterminator="\n", low_memory=False)
bad = pd.read_csv(path_names + "disinformation_users.csv", lineterminator="\n", low_memory=False)
words_custom = pd.read_csv(path_names + "words_to_remove.csv", lineterminator="\n", low_memory=False)
good = runSage.clean_data_format(good)
bad = runSage.clean_data_format(bad)
dozen_names = list(good["screen_name"])
dozen_names.extend(list(bad["screen_name"]))
dozen_names.extend(list(words_custom["word"]))
dozen_names = [item.lower() for item in dozen_names]
print(len(dozen_names))


def clean_cached(text):
    text = ' '.join([word for word in text.split() if word not in cachedStopWords])
    text = ' '.join([word for word in text.split() if word not in dozen_names])
    return text


# def clean_stop_words(text):
#     text_tokens = word_tokenize(text)
#     string = ""
#     for word in text_tokens:
#         if word not in stopwords.words():
#             string += word + " "
#     return string


def write_file(df: pd.DataFrame, name: str):
    text_file = open(f"{name}.txt", "w", encoding="utf-8")
    for i in df["text"]:
        content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', i)
        content = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", content).split())
        content = re.sub('[^a-zA-Z0-9\s]', '', content)
        content = content.lower()
        content = clean_cached(content)
        text_file.write(content + "\n")
    text_file.close()


def main():
    cols = ["text", "user_screen_name"]
    df_good = pd.read_csv(path + "good_dozen.csv", lineterminator="\n", low_memory=False, usecols=cols)
    write_file(df_good, "data/good")
    print("Good Done...")
    df_bad = pd.read_csv(path + "ccdh_tweets.csv", lineterminator="\n", low_memory=False, usecols=cols)
    write_file(df_bad, "data/bad")
    print("Bad Done...")

    # lst = ["rashid", "kellybroganmd", "buttar", "drtedros", "ashishkjha", "unhealthytruth", "brogan", "mercola",
    #        "drmikeryan", "edyong209", "mlipsitch", "helenbranswell"]
    # df = pd.DataFrame(lst, columns=["word"])
    # df.to_csv(path_names + "words_to_remove.csv", index=False, encoding="utf-8", line_terminator="\n")


if __name__ == '__main__':
    main()
