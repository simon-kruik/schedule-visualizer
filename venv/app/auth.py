#
#
#
#
import os
import json
import adal
import uuid
import requests
import urllib
from flask import request, session


def handle_auth_response(request, state):
    data = request.form.to_dict()
    # print("Data returned: " + str(data))
    # print("Current session state: " + session['state'])
    if 'state' in data:
        if data['state'] == state:
            return True
    else:
        print("Failure")
        return False


def load_auth_details(Auth_File_Name):
    Auth_File = open(Auth_File_Name, 'r')
    Auth_Details = json.load(Auth_File)
    return Auth_Details


def get_authorization_device_code(auth_context, resource, app_id):
    code = auth_context.acquire_user_code(resource, app_id)
    # KEYS IN CODE DICTIONARY
    # user_code
    # device_code
    # verification_url
    # expires_in
    # interval
    # message
    # correlation_id
    # print(code['message'])
    token_dict = auth_context.acquire_token_with_device_code(resource, code, app_id)
    return token_dict


def get_authorization_user_pass(resource, username, password, app_id):
    token_dict = auth_context.acquire_token_with_username_password(resource, username, password, app_id)
    return token_dict


def get_authorization_web(aad_tenant_domain, app_id, permissions, state):
    permissions_urls = []
    for x in permissions:
        permissions_urls.append("https://graph.microsoft.com/" + x)
    permissions_string = "%20".join(permissions_urls)
    # state = str(uuid.uuid4())
    # session['state'] = state
    endpoint = "https://login.microsoftonline.com/" + aad_tenant_domain + "/oauth2/v2.0/authorize/?client_id=" + app_id + "&response_type=code&redirect_uri=http://localhost:5000/login/authorized&response_mode=form_post&scope=offline_access%20" + permissions_string + "&state=" + state
    return endpoint


def get_token_endpoint_web(aad_tenant_domain, app_id, permissions, code, app_secret):
    permissions_urls = []
    for x in permissions:
        permissions_urls.append("https://graph.microsoft.com/" + x)
    permissions_string = "%20".join(permissions_urls)
    # state = str(uuid.uuid4())
    # Session['state'] = state
    endpoint = "https://login.microsoftonline.com/" + aad_tenant_domain + "/oauth2/v2.0/token"
    app_secret = urllib.parse.quote_plus(app_secret)
    redirect_uri = "http://localhost:5000/login/authorized"
    form_data = "grant_type=authorization_code&client_id=" + app_id + "&scope=offline_access%20" + permissions_string + "&code=" + code + "&redirect_uri="+ redirect_uri +"&client_secret=" + app_secret
    # form_data = urllib.parse.quote_plus(raw_form_data)
    data = {"endpoint":endpoint, "form_data":form_data}
    # print("Raw Form Data: " + raw_form_data)
    # print("Parsed Form Data: " + form_data)
    return data


def get_token_web(data):
    url = data["endpoint"]
    headers = {"Content-Type":"application/x-www-form-urlencoded"}
    payload = data["form_data"]
    results = requests.post(url=url, headers=headers, data=str(payload))
    # print(results.text)
    return json.loads(results.text)


def refresh_access_token(aad_domain, ref_token, app_id, app_secret, redirect_uri, permissions):
    permissions_urls = []
    for x in permissions:
        permissions_urls.append("https://graph.microsoft.com/" + x)
    permissions_string = "%20".join(permissions_urls)
    endpoint = "https://login.microsoftonline.com/" + aad_domain + "/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    app_secret = urllib.parse.quote_plus(app_secret)
    payload = "client_id=" + app_id + "&scope=offline_access%20" + permissions_string + "&refresh_token=" + ref_token + "&redirect_uri" + redirect_uri + "&grant_type=refresh_token&client_secret=" + app_secret
    results = requests.post(url=endpoint,headers=headers,data=payload)
    # print(results.text)
    return results.text
