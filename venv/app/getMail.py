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
    mail_folders = json.loads(results.text)['value']
    occupied_mail_folders = []
    for item in mail_folders:
        if (item["totalItemCount"] > 0):
            occupied_mail_folders.append(item)
    return occupied_mail_folders

def search_folders(access_token, choice_dictionary, user="me"):
    start_date = choice_dictionary['Start Date']
    end_date = choice_dictionary['End Date']
    folder_id = choice_dictionary['folder_id']
    direction = choice_dictionary['stats']
    stat_type = choice_dictionary['stat_type']
    url = "https://graph.microsoft.com/v1.0/" + user + '/mailfolders/"' + folder_id + '"/messages?$select=sender&$filter=receivedDateTime ge ' + start_date + " and receivedDateTime lt " + end_date
    senders = paginate(access_token, url)
    #print("Senders: ",senders)
    if (stat_type == "faculty"):
        results = analyse_faculty(access_token,senders)
    else:
        results = None
    # Need to figure out difference between senders and recipients depending on the direction variable
    return results


def paginate(access_token, url):
    values = []
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    curr_results = json.loads(results.text)
    if "@odata.nextLink" in curr_results:
        values = values + paginate(access_token,curr_results["@odata.nextLink"])
    values = values + curr_results["value"]
    return values

    # Grab just the senders into a big list, and recursively call if there's an odata.nextlink
    return results

def analyse_faculty(access_token, senders):
    faculties = {}
    for item in senders:
        if '@uts.edu.au' in item['sender']['emailAddress']['address']:
                faculty = lookup_faculty_staff(access_token,item['sender']['emailAddress']['address'])
                if faculty in faculties:
                    faculties[faculty] = faculties[faculty] + 1
                else:
                    faculties[faculty] = 1
    return faculties

def lookup_faculty_staff(access_token, email_address):
    url = "https://graph.microsoft.com/v1.0/users/" + email_address + "?$select=displayName,jobTitle,onPremisesExtensionAttributes"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    results = json.loads(results.text)
    print(results)
    if 'error' in results:
        return 'Other'
    else:
        return results['onPremisesExtensionAttributes']['extensionAttribute1']

def test_function(access_token,choice_dict):
    url = "https://graph.microsoft.com/v1.0/users/Pascal.Tampubolon@uts.edu.au?$select=displayName,jobTitle,onPremisesExtensionAttributes"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    results = json.loads(results.text)
    return results

def lookup_department_staff(access_token,email_address):
    url = "https://graph.microsoft.com/v1.0/users/" + email_address + "?$select=displayName,jobTitle,department"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    results = json.loads(results.text)
    print(results)
    if 'error' in results:
        return 'Other'
    else:
        return results['department']
