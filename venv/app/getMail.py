"""
An email analysis tool to see what units you've been sending emails to.

Ideal output: JSON file summarising email interactions

"""

# For sending and receiving data over HTTP
import requests
# For dealing with the received data
import json

def get_users_folders(access_token, user="me"):
    url = "https://graph.microsoft.com/v1.0/" + user + "/mailFolders"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    #print(results.text)
    return json.loads(results.text)['value']
