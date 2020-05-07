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
        url = "https://graph.microsoft.com/v1.0/users/" + id + "/photos('120x120')/$value"
        headers = {
            "Authorization": "Bearer " + access_token,
            "Host" : "graph.microsoft.com"
        }
        results = requests.get(url=url, headers=headers)
        photo = results.content
    else:
        photo = False
    if "error" in str(photo):
        return False
    return photo

def get_coworker_emails(access_token):
    manager_url = "https://graph.microsoft.com/v1.0/me/manager"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host" : "graph.microsoft.com"
    }
    manager_results = requests.get(url=manager_url, headers=headers)
    manager = json.loads(manager_results.text)
    manager_id = manager['id']

    coworkers_url = "https://graph.microsoft.com/v1.0/users/" + manager_id + "/directreports"
    coworkers_results = requests.get(url=coworkers_url, headers=headers)
    coworkers = json.loads(coworkers_results.text)
    coworker_emails = [manager['mail']]
    for coworker in coworkers['value']:
        coworker_emails.append(coworker['mail'])
    return coworker_emails

def test_get_photo():
    with open('static/img/test.jfif') as f:
        print(f)
