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

def get_id(email, access_token):
    url = "https://graph.microsoft.com/v1.0/users/" + email
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    if "id" in json.loads(results.text):
        id = json.loads(results.text)['id']
    else:
        id = False
    return id

def get_photo(email, access_token):
    id = get_id(email, access_token)
    if (id):
        url = "https://graph.microsoft.com/v1.0/users/" + id + "/photo/$value"
        headers = {
            "Authorization": "Bearer " + access_token,
            "Host" : "graph.microsoft.com"
        }
        results = requests.get(url=url, headers=headers)
        photo = results.content
        print(photo)
    else:
        photo = False
    return photo

def test_get_photo():
    with open('static/img/test.jfif') as f:
        print(f)
