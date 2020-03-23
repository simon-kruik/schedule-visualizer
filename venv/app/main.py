#
#   Microsoft Graph Schedules Visualiser
#   Created by Simon Kruik, starting 2019-01-07
#

import json
import hashlib
import hmac
import base64
import datetime
import uuid
import requests
import re
from adal import AuthenticationContext
import auth
import getSchedule, getProfile


auth_context = AuthenticationContext("https://login.microsoftonline.com/studentutsedu.onmicrosoft.com")
auth_details = auth.load_auth_details("AAD_Auth.json")

def format_date(date):
    return date.strftime("%Y-%m-%dT%H:%M:%S")


def get_current_date():
    return datetime.datetime.utcnow()


def get_auth_link(state):
    auth_details = auth.load_auth_details("AAD_Auth.json")
    aad_tenant_domain = auth_details["AAD-Domain"]
    permissions = auth_details["Permissions"]
    app_id = auth_details["App-ID"]
    # resource = "https://graph.microsoft.com"
    return auth.get_authorization_web(aad_tenant_domain, app_id, permissions, state)


def get_token_web(request):
    data = request.form.to_dict()
    code = data['code']
    secret = auth_details["Secret"]
    app_id = auth_details["App-ID"]
    permissions = auth_details["Permissions"]
    domain = auth_details["AAD-Domain"]
    data = auth.get_token_endpoint_web(domain, app_id, permissions, code, secret)
    token_data = auth.get_token_web(data)
    return token_data


def get_refreshed_token(refresh_token):
    aad_domain = auth_details['AAD-Domain']
    ref_token = refresh_token
    app_id = auth_details["App-ID"]
    app_secret = auth_details["Secret"]
    redirect_uri = auth_details["Redirect-URI"]
    permissions = auth_details["Permissions"]
    results = json.loads(auth.refresh_access_token(aad_domain, ref_token, app_id, app_secret, redirect_uri, permissions))
    return results

def verify_profiles(profiles_string, access_token):
    email_pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    profiles = profiles_string.split(',')
    emails = []
    for profile in profiles:
        emails.append(profile.strip())
    for email in emails:
        if email_pattern.match(email):
            data = getProfile.profile_exists(email, access_token)
            if "id" not in data:
                print("EMAIL FAILED API CHECK: " + email)
                return False
        else:
            print("EMAIL FAILED REGEX CHECK: " + email)
            return False
    # print("verify_profiles: None failed")
    return emails


def getSchedules(emails, access_token):
    users = {}
    for email in emails:
        current_dict = {"email": email}
        schedule = getSchedule.getSchedule()
        busy = getSchedule.isBusy(schedule)
        next_free = getSchedule.nextFree(schedule)
        users["email"] = current_dict
    return users



if __name__ == '__main__':
    auth_details = auth.load_auth_details("authDetails.json")
    aad_tenant_domain = auth_details["AAD-Domain"]
    app_id = auth_details["App-ID"]
    permissions = auth_details["Permissions"]
    username = auth_details["username"]
    password = auth_details["password"]
    resource = "https://graph.microsoft.com"
    time_zone = "UTC"
    interval = 15
    token_dict = auth.get_authorization_device_code(auth_context, resource, app_id)
    access_token = token_dict["tokenType"] + " " + token_dict["accessToken"]
    user_id = token_dict["userId"]

    date_dict = get_current_date()

    print(date_dict["date_string"])

    # print(get_authorization_user_pass(resource, username, password, app_id))
    # print(get_authorization_web(aad_tentant_domain,app_id,permissions))

    # token_response = auth_context.acquire_token_with_authorization_code
    current_date = date_dict["date_string"]
    week_date = date_dict["date"] + datetime.timedelta(days=7)
    next_date = week_date.strftime("%Y-%m-%dT%H:%M:%S")

    testSchedule = get_schedule(access_token, user_id, current_date, next_date, time_zone, interval)
    print(testSchedule.text)
