import requests
import datetime
import json
import time

timezones_file = "timezones.json"

OUT = "Out"
BUSY = "Busy"
TENTATIVE = "Tentative"
FREE = "Free"

# Separation between Start_Date and End_Date needs to be 30 minutes or morel


# Simply submits the request to Microsoft Graph API and returns the resulting JSON object
def get_schedule(access_token, user, start_date, end_date, time_zone):
    url = "https://graph.microsoft.com/beta/me/calendar/getschedule"
    payload = {
        "Schedules": [user],
        "StartTime": {
            "dateTime": start_date,
            "timeZone": time_zone
        },
        "EndTime": {
            "dateTime": end_date,
            "timeZone": time_zone
        }
    }

    headers = {
        "Authorization": access_token,
        "Host": "graph.microsoft.com",
        "Content-type": "application/json"
    }
    results = requests.post(url=url, headers=headers, data=str(payload))
    return results

# Checks if the given time is within working hours, and not during any events for the given schedule
def isBusy(schedule, given_time):
    # Dissecting the schedule object
    given_time = given_time.astimezone(datetime.timezone.utc)
    schedules = schedule["value"]
    details = schedules[0]
    items = details["scheduleItems"]
    workdays = details["workingHours"]
    # Comparing the given time to the working hours in the schedule
    given_day_string = given_time.strftime("%A")
    if given_day_string.lower() not in workdays["daysOfWeek"]:
        print("Not a working day")
        return OUT
    start_time = parse_working_hours_time(workdays["startTime"], workdays["timeZone"]["name"]).astimezone(datetime.timezone.utc)
    end_time = parse_working_hours_time(workdays["endTime"], workdays["timeZone"]["name"]).astimezone(datetime.timezone.utc)
    print(str(start_time.time()))
    print(str(given_time.time()))
    print(str(end_time.time()))
    # This isn't working as expected...
    if end_time.time() <= given_time.time() <= start_time.time():
        return OUT

    # Comparing the
    for item in items:
        return FREE
    # for item in items.items()
    #   if
    return FREE

# The returned working hours include a timezone, that we need to parse to UTC, it does this by loading a file,
def parse_working_hours_time(time_string, time_zone):
    if time_zone == "Customized Time Zone":
        print("Oh no!")
    tz_file = open(timezones_file, 'r')
    tz_dict = json.load(tz_file)
    if time_zone in tz_dict:
        offset_dict = tz_dict[time_zone]
    else:
        offset_dict = {"sign":"+","hours":"00","minutes":"00"}
    tz_string = offset_dict["sign"] + offset_dict["hours"] + offset_dict["minutes"]
    combo_string = time_string[:-1] + tz_string
    given_time = datetime.datetime.strptime(combo_string, "%H:%M:%S.%f%z")
    return given_time
