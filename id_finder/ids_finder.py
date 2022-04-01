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
api = tweepy.API(auth, wait_on_rate_limit=True)

data = pd.read_csv("./username_to_id/try.csv")
list_name = list(data["user_screen_name"])

ids = []
cont = 0
for i in tqdm(list_name):
    try:
        user = api.get_user(screen_name=i)
        ids.append(user.id)
    except tweepy.errors.NotFound as e:
        # print("Tweepy Error: {}".format(e))
        ids.append(e.api_errors)
    except tweepy.errors.Forbidden as e:
        # print("Tweepy Error: {}".format(e))
        ids.append(e.api_errors)
    except tweepy.errors.TooManyRequests as e:
        print("Tweepy Error: {}".format(e))

pd.DataFrame(list(zip(ids, list_name)), columns=["userid", "user_screen_name"]) \
    .to_csv("username_to_id/result.csv", line_terminator="\n", encoding="utf-8", index=False)
