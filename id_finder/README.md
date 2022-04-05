# Id finder for Twitter

### How to run

<pre><code> python ids_finder.py "filename" </code></pre>

### General info

- **filename**: this specifies the file which contains usernames, the input file MUST be in csv format with the "user_screen_name" field.
- results are placed into **result.csv** file, in **username_to_id** directory

### Auth
```
{
  "Authorization": "Bearer xxxxxxx",
  "guest_id": "xxxxxxx",
  "personalization_id": "xxxxxxx",
  "consumer_key": "xxxxxxx",
  "consumer_secret": "xxxxxxx",
  "access_token":"xxxxxxx",
  "access_token_secret": "xxxxxxx"
}
```
For **_ids_finder.py_** consumer_key, consumer_secret, access_token, access_token_secret are **required**.
