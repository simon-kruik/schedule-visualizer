import requests
import datetime
import json
import time
import dateutil.parser

timezones_file = "timezones.json"
treat_tentative_as_busy = True

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
    # print(results.json()) # Testing
    return results.json()


def parse_schedule_event_hours(time_string, timezone_string):
    if timezone_string == "Customized Time Zone":
        print("Oh no!")
        print(timezone_string)
    tz_file = open(timezones_file, 'r')
    tz_dict = json.load(tz_file)
    if timezone_string in tz_dict:
        offset_dict = tz_dict[timezone_string]
    else:
        offset_dict = {"sign":"+","hours":"00","minutes":"00"}
    tz_string = offset_dict["sign"] + offset_dict["hours"] + offset_dict["minutes"]
    # Using dateutil.parser.isoparse cause it's way more reliable than datetime's ISO parser
    converted_datetime = dateutil.parser.isoparse(time_string)
    time_zone_delta = datetime.timedelta(hours=int(offset_dict['hours']), minutes=int(offset_dict['minutes']))
    if (offset_dict['sign'] == "+"):
        converted_datetime = converted_datetime + time_zone_delta
    else:
        converted_datetime = converted_datetime - time_zone_delta
    converted_datetime = converted_datetime.replace(tzinfo=datetime.timezone.utc)
    return converted_datetime


# Checks if the given time is within working hours, and not during any events for the given schedule
def isBusy(schedule, given_time):
    # Dissecting the schedule object

    # Want to deal with everything in UTC, so convert given time - need to test on actual values
    given_time_UTC = given_time.astimezone(datetime.timezone.utc)
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
    #print(str(start_time.time()))
    #print(str(given_time.time()))
    #print(str(end_time.time()))
    # Inverted comparison to check
    if end_time.time() <= given_time_UTC.time() <= start_time.time():
        return OUT

    # Comparing the list of meetings to current time
    for item in items:
        if (item['status'] == 'busy' or (treat_tentative_as_busy and item['status'] == 'tentative')):
            start_time = parse_schedule_event_hours(item['start']['dateTime'],item['start']['timeZone'])
            end_time = parse_schedule_event_hours(item['end']['dateTime'], item['end']['timeZone'])
            if end_time >= given_time_UTC >= start_time:
                return BUSY # figure out how to convert schedule items times to datetime objects in UTC

    return FREE

# Function to find when a person will next be available
def next_free(schedule, given_time):
    # Dissecting the schedule object

    # Want to deal with everything in UTC, so convert given time - need to test on actual values
    given_time_UTC = given_time.astimezone(datetime.timezone.utc)
    schedules = schedule["value"]
    details = schedules[0]
    items = details["scheduleItems"]



# The returned working hours include a timezone, that we need to parse to UTC, it does this by loading a file,
def parse_working_hours_time(time_string, time_zone):
    if time_zone == "Customized Time Zone":
        print("Oh no!")
        print(time_zone)
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
