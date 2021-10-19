import nltk
import pandas as pd
import glob
import re
from nltk.corpus import stopwords

path = glob.glob("C:/Users/gianl/Desktop/Gi/Supsi/BachelorProject/large_files/ccdh/")[0]
cachedStopWords = stopwords.words("english")


def clean_cached(text):
    text = ' '.join([word for word in text.split() if word not in cachedStopWords])
    return text


# def clean_stop_words(text):
#     text_tokens = word_tokenize(text)
#     string = ""
#     for word in text_tokens:
#         if word not in stopwords.words():
#             string += word + " "
#     return string


def write_file(df: pd.DataFrame, name: str):
    content = ""
    text_file = open(f"{name}.txt", "w", encoding="utf-8")
    for i in df["text"]:
        if "http" in i:
            m = re.search(r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])', i)
            if m:
                content = i.replace(m.group(0), '')
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


if __name__ == '__main__':
    main()
