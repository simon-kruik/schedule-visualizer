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

def get_parent(access_token, group_id, item_id):
    url = "https://graph.microsoft.com/v1.0/groups/" + group_id + "/drive/items/" + item_id
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    #print(results.text)
    result_dict = json.loads(results.text)
    try:
        return (result_dict['parentReference']['id'],result_dict['parentReference']['path'].split('/')[-1])
    except:
        return (None, get_group_name(access_token, group_id))

def get_path_tuples(access_token, group_id, item_id):
    tuple_list = [(item_id,get_item_name(access_token,group_id,item_id))]
    parent_tuple = get_parent(access_token, group_id, item_id)
    tuple_list.append(parent_tuple)
    while parent_tuple[0] is not None:
        parent_tuple = get_parent(access_token, group_id, parent_tuple[0])
        tuple_list.append(parent_tuple)
    tuple_list.reverse()
    #print(tuple_list)
    return tuple_list

def get_item_name(access_token, group_id, item_id):
    url = "https://graph.microsoft.com/v1.0/groups/" + group_id + "/drive/items/" + item_id
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    result_dict = json.loads(results.text)
    return result_dict['name']

def get_group_name(access_token, group_id):
    url = "https://graph.microsoft.com/v1.0/groups/" + group_id + '/drive/'
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    result_dict = json.loads(results.text)
    print(result_dict)
    return result_dict['owner']['group']['displayName']
