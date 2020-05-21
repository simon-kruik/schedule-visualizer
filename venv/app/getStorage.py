"https://graph.microsoft.com/v1.0/groups/0c0f97ad-aaf4-443f-9ffc-02c1fbc6a812/drive/root/children"


import requests
import json

def get_root_children(access_token, group_id):
    url = "https://graph.microsoft.com/v1.0/groups/" + group_id + "/drive/root/children"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    #print(results.text)
    return json.loads(results.text)['value']

def get_root_folders(access_token, group_id):
    folders = []
    children = get_root_children(access_token,group_id)
    for item in children:
        if 'folder' in item:
            folders.append(item)
    return folders


def get_item_children(access_token, group_id, folder_id):
    url = "https://graph.microsoft.com/v1.0/groups/" + group_id + "/drive/items/" + folder_id + "/children"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    return json.loads(results.text)['value']



def get_child_folders(access_token, group_id, folder_id):
    folders = []
    children = get_item_children(access_token,group_id, folder_id)
    for item in children:
        if 'folder' in item:
            folders.append(item)
    return folders
