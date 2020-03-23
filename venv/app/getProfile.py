import json
import requests


def get_profile(access_token):
    # print("Access Token: " + access_token)
    url = "https://graph.microsoft.com/v1.0/me"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    # print(results.text)
    return json.loads(results.text)

def profile_exists(email, access_token):
    url = "https://graph.microsoft.com/v1.0/users/" + email
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    # print("API Result for email " + email + " : " + results.text)
    return json.loads(results.text)
