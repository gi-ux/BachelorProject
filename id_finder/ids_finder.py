import tweepy
import pandas as pd
import json
from tqdm import tqdm

jsonFile = open('auth.json', 'r')
config = json.load(jsonFile)
jsonFile.close()

consumer_key = config["consumer_key"]
consumer_secret = config["consumer_secret"]
access_token = config["access_token"]
access_token_secret = config["access_token_secret"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

data = pd.read_csv("./username_to_id/sample_2000_tail_bad.csv")
list_name = list(data["user_screen_name"])

ids = []
cont = 0
for i in tqdm(list_name):
    try:

        if cont == 85:
            break
        user = api.get_user(screen_name=i)
        ids.append(user.id)
        if cont > 85:
            print(user.id)
        cont += 1
    except tweepy.errors.NotFound as e:
        print("Tweepy Error: {}".format(e))
    except tweepy.errors.Forbidden as e:
        print("Tweepy Error: {}".format(e))
    except tweepy.errors.TooManyRequests as e:
        print("Tweepy Error: {}".format(e))

pd.DataFrame(list(zip(ids, list_name)), columns=["userid", "user_screen_name"]) \
    .to_csv("username_to_id/result_tail.csv", line_terminator="\n", encoding="utf-8", index=False)
