"""
An email analysis tool to see what units you've been sending emails to.

Ideal output: JSON file summarising email interactions

"""

# For sending and receiving data over HTTP
import requests
# For dealing with the received data
import json


# Returns a list of folders from the user
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



# Grabs the start and end date from the choices, then returns a list of all "value" items from the request.
def search_senders(access_token, choice_dictionary, user="me"):
    start_date = choice_dictionary['Start Date']
    end_date = choice_dictionary['End Date']
    folder_id = choice_dictionary['sent_folder_id']
    stat_type = choice_dictionary['stat_type']
    url = "https://graph.microsoft.com/v1.0/" + user + '/mailfolders/"' + folder_id + '"/messages?$select=sender&$filter=receivedDateTime ge ' + start_date + " and receivedDateTime lt " + end_date
    senders = paginate(access_token, url)
    return senders

# Grabs the start and end date from the choices, then returns a list of all "value" items from the request.
def search_recipients(access_token, choice_dictionary, user="me"):
    start_date = choice_dictionary['Start Date']
    end_date = choice_dictionary['End Date']
    folder_id = choice_dictionary['received_folder_id']
    stat_type = choice_dictionary['stat_type']
    url = "https://graph.microsoft.com/v1.0/" + user + '/mailfolders/"' + folder_id + '"/messages?$select=toRecipients&$filter=receivedDateTime ge ' + start_date + " and receivedDateTime lt " + end_date
    recipients = paginate(access_token, url)
    return recipients


# The paginate function takes a URL and recursively returns the "value" list of the dictionary added to any previous "value" lists until there's no more data to get.
# Resulting in one huge long list of whatever object you're requesting
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


# This function handles the choices from the form, and calls and collates results from the relevant functions then returns a dict pf the stats
def handle_choices(access_token,choice_dict, user="me"):
    addresses = []
    if choice_dict["received_folder_id"] != "None":
        addresses = addresses + search_recipients(access_token, choice_dict)
    if choice_dict["sent_folder_id"] != "None":
        addresses = addresses + search_senders(access_token, choice_dict)
    if choice_dict["stat_type"] == "faculty":
        stats = analyse_faculty(access_token,addresses)
    if "exclude_own_faculty" in choice_dict:
        own_faculty = lookup_own_level_one(access_token)
        stats.pop(own_faculty,None)
    return stats

def analyse_faculty(access_token, items):
    faculties = {}
    user_faculty_dict = {}
    for item in items:
        if 'sender' in item:
            if '@uts.edu.au' in item['sender']['emailAddress']['address']:
                if item['sender']['emailAddress']['address'] in user_faculty_dict:
                    faculty = user_faculty_dict[item['sender']['emailAddress']['address']]
                else:
                    faculty = lookup_level_one_staff(access_token,item['sender']['emailAddress']['address'])
                if faculty in faculties:
                    faculties[faculty] = faculties[faculty] + 1
                else:
                    faculties[faculty] = 1
        elif 'toRecipients' in item:
            for recipient in item['toRecipients']:
                if '@uts.edu.au' in recipient['emailAddress']['address']:
                    if recipient['emailAddress']['address'] in user_faculty_dict:
                        faculty = user_faculty_dict[recipient['emailAddress']['address']]
                    else:
                        faculty = lookup_level_one_staff(access_token,recipient['emailAddress']['address'])
                    if faculty in faculties:
                        faculties[faculty] = faculties[faculty] + 1
                    else:
                        faculties[faculty] = 1
    return faculties


# def analyse_faculty_sender(access_token, senders):
#     faculties = {}
#     user_faculty_dict = {}
#         if '@uts.edu.au' in :
#             if item['sender']['emailAddress']['address'] in user_faculty_dict:
#                 faculty = user_faculty_dict[item['sender']['emailAddress']['address']]
#             else:
#                 faculty = lookup_level_one_staff(access_token,item['sender']['emailAddress']['address'])
#                 user_faculty_dict[item['sender']['emailAddress']['address']] = faculty
#             if faculty in faculties:
#                 faculties[faculty] = faculties[faculty] + 1
#             else:
#                 faculties[faculty] = 1
#     return faculties
#
# def analyse_faculty_recipient(access_token, recipients):
#     faculties = {}
#     user_faculty_dict = {}
#     for item in recipients:
#         if '@uts.edu.au' in item['sender']['emailAddress']['address']:
#                 if item['sender']['emailAddress']['address'] in user_faculty_dict:
#                     faculty = user_faculty_dict[item['sender']['emailAddress']['address']]
#                 else:
#                     faculty = lookup_level_one_staff(access_token,item['sender']['emailAddress']['address'])
#                     user_faculty_dict[item['sender']['emailAddress']['address']] = faculty
#                 if faculty in faculties:
#                     faculties[faculty] = faculties[faculty] + 1
#                 else:
#                     faculties[faculty] = 1
#     return faculties

def lookup_own_level_one(access_token):
    url = "https://graph.microsoft.com/v1.0/me " + "?$select=displayName,jobTitle,onPremisesExtensionAttributes"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    results = json.loads(results.text)
    if 'error' in results:
        return 'Other'
    else:
        return results['onPremisesExtensionAttributes']['extensionAttribute1']

def lookup_level_one_staff(access_token, email_address):
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

def lookup_level_two_staff(access_token, email_address):
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
        return results['onPremisesExtensionAttributes']['extensionAttribute2']


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


def test_function(access_token,choice_dict):
    url = "https://graph.microsoft.com/v1.0/users/Pascal.Tampubolon@uts.edu.au?$select=displayName,jobTitle,onPremisesExtensionAttributes"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Host": "graph.microsoft.com"
    }
    results = requests.get(url=url, headers=headers)
    results = json.loads(results.text)
    return results
