#
#   Microsoft Graph Schedules Visualiser
#   Created by Simon Kruik, starting 2019-01-07
#

import json
import hashlib
import hmac
import base64
import datetime
from datetime import timedelta
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


# For validating the emails submitted in /schedule/choose page
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
    start_date = format_date(get_current_date())
    end_date = format_date(get_current_date() + timedelta(days=5))
    timezone = "Australia\\Sydney"
    print(start_date)
    print(end_date)
    users = {}
    for email in emails:
        current_dict = {"email": email}
        schedule = getSchedule.get_schedule(access_token, email, start_date, end_date, timezone)
        current_dict['busy'] = getSchedule.isBusy(schedule,get_current_date())
        current_dict['next_free'] = getSchedule.nextFree(schedule)
        users[email] = current_dict
    return users



if __name__ == '__main__':
    schedule = {
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#Collection(microsoft.graph.scheduleInformation)",
    "value": [
        {
            "scheduleId": "Pascal.tampubolon@uts.edu.au",
            "availabilityView": "0000000000000100222200000000000000000000000000000000000222222222000220200000000000000000000000000000000002222200000222220000000000000000000000000000000222222222222222220000000000000000000000000000000000000000000000000000000000000000000000000",
            "scheduleItems": [
                {
                    "status": "tentative",
                    "start": {
                        "dateTime": "2020-03-24T01:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-24T01:15:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-24T02:30:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-24T04:00:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-24T22:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-25T01:00:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-24T23:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-24T23:30:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "tentative",
                    "start": {
                        "dateTime": "2020-03-25T01:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-25T01:15:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-25T01:30:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-25T02:00:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-25T04:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-25T04:30:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "tentative",
                    "start": {
                        "dateTime": "2020-03-25T04:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-25T04:45:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-25T05:30:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-25T05:45:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-25T23:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-25T23:30:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-25T23:30:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-26T00:00:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-26T00:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-26T00:30:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-26T00:30:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-26T01:00:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "tentative",
                    "start": {
                        "dateTime": "2020-03-26T01:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-26T01:15:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-26T04:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-26T05:00:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-26T05:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-26T06:00:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-26T22:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-27T06:00:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "tentative",
                    "start": {
                        "dateTime": "2020-03-27T01:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-27T01:15:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-27T01:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-27T02:30:00.0000000",
                        "timeZone": "UTC"
                    }
                },
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2020-03-27T01:30:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2020-03-27T02:00:00.0000000",
                        "timeZone": "UTC"
                    }
                }
            ],
            "workingHours": {
                "daysOfWeek": [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday"
                ],
                "startTime": "08:00:00.0000000",
                "endTime": "17:00:00.0000000",
                "timeZone": {
                    "name": "AUS Eastern Standard Time"
                }
            }
        }
    ]
    }
    print(getSchedule.isBusy(schedule, get_current_date()))
    #getSchedules({'fake'},'fake')









    #
    # auth_details = auth.load_auth_details("authDetails.json")
    # aad_tenant_domain = auth_details["AAD-Domain"]
    # app_id = auth_details["App-ID"]
    # permissions = auth_details["Permissions"]
    # username = auth_details["username"]
    # password = auth_details["password"]
    # resource = "https://graph.microsoft.com"
    # time_zone = "UTC"
    # interval = 15
    # token_dict = auth.get_authorization_device_code(auth_context, resource, app_id)
    # access_token = token_dict["tokenType"] + " " + token_dict["accessToken"]
    # user_id = token_dict["userId"]
    # print("Test")
    # date_dict = get_current_date()
    #
    # print(date_dict["date_string"])
    #
    # # print(get_authorization_user_pass(resource, username, password, app_id))
    # # print(get_authorization_web(aad_tentant_domain,app_id,permissions))
    #
    # # token_response = auth_context.acquire_token_with_authorization_code
    # current_date = date_dict["date_string"]
    # week_date = date_dict["date"] + datetime.timedelta(days=7)
    # next_date = week_date.strftime("%Y-%m-%dT%H:%M:%S")
    #
    # testSchedule = get_schedule(access_token, user_id, current_date, next_date, time_zone, interval)
    # print(testSchedule.text)
