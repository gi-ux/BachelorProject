import requests
import pandas as pd
import json

jsonFile = open('auth.json', 'r')
config = json.load(jsonFile)
jsonFile.close()

bearer_token = config["Authorization"]
guest_id = config["guest_id"]
personalization_id = config["personalization_id"]

# data = pd.read_csv("id_to_username/to_find.csv")
data = pd.read_csv("C:/Users/gianl/Desktop/Gi/Supsi/TwitterTransparencyData/output_files/bad_exposure.csv")
list_id = list(data["user"])
chunks = [list_id[x:x+100] for x in range(0, len(list_id), 100)]
count = 0
for chunk in chunks:
    string_ids = ""
    for i in range(len(chunk)):
        if i == len(chunk) - 1:
            string_ids = string_ids + str(chunk[i])
        else:
            string_ids = string_ids + str(chunk[i]) + ","
    url = "https://api.twitter.com/2/users?ids=" + string_ids

    payload = {}
    Cookie = str('guest_id=' + guest_id + "; " + "personalization_id=" + personalization_id)
    headers = {
        'Authorization': bearer_token,
        'Cookie': Cookie
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response.raise_for_status()
    with open(f"username_to_id/output_{count}.json", "wb") as f:
        f.write(response.text.encode())
    count += 1