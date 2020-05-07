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

def is_in_working_hours(schedule, given_time):
    #print("Given_time originally",given_time)
    given_time_UTC = given_time.astimezone(datetime.timezone.utc)
    #print("Given_time in UTC", given_time_UTC)
    schedules = schedule["value"]
    details = schedules[0]
    workdays = details["workingHours"]

    # Comparing the given time to the working hours in the schedule
    given_day_string = given_time.strftime("%A")
    if given_day_string.lower() not in workdays["daysOfWeek"]:
        return False
    start_time = parse_working_hours_time(workdays["startTime"], workdays["timeZone"]["name"]).astimezone(datetime.timezone.utc)
    end_time = parse_working_hours_time(workdays["endTime"], workdays["timeZone"]["name"]).astimezone(datetime.timezone.utc)
    # Inverted comparison to check
    if end_time.time() <= given_time_UTC.time() <= start_time.time():
        return False
    return True


# Checks if the given time is within working hours, and not during any events for the given schedule
def isBusy(schedule, given_time):
    # Dissecting the schedule object

    # Want to deal with everything in UTC, so convert given time - need to test on actual values
    given_time_UTC = given_time.astimezone(datetime.timezone.utc)
    schedules = schedule["value"]
    details = schedules[0]
    items = details["scheduleItems"]
    #print(str(start_time.time()))
    #print(str(given_time.time()))
    #print(str(end_time.time()))

    if not (is_in_working_hours(schedule,given_time)):
        return OUT

    # Comparing the list of meetings to current time
    for item in items:
        if (item['status'] == 'busy' or (treat_tentative_as_busy and item['status'] == 'tentative')):
            start_time = parse_schedule_event_hours(item['start']['dateTime'],item['start']['timeZone'])
            end_time = parse_schedule_event_hours(item['end']['dateTime'], item['end']['timeZone'])
            if end_time >= given_time_UTC >= start_time:
                return BUSY # figure out how to convert schedule items times to datetime objects in UTC

    return FREE



def get_items_sorted_by_end_times(schedule):
    schedules = schedule["value"]
    details = schedules[0]
    items = details["scheduleItems"]
    sorted_items = sorted(items, key = lambda item: dateutil.parser.isoparse(item["end"]["dateTime"]))
    return sorted_items

def get_items_sorted_by_start_times(schedule):
    schedules = schedule["value"]
    details = schedules[0]
    items = details["scheduleItems"]
    sorted_items = sorted(items, key = lambda item: dateutil.parser.isoparse(item["start"]["dateTime"]))
    return sorted_items

def parse_start_time(item):
    if item['start']['timeZone'] == "UTC":
        return dateutil.parser.isoparse(item["start"]["dateTime"]).replace(tzinfo=datetime.timezone.utc)

def parse_end_time(item):
    if item['end']['timeZone'] == "UTC":
        return dateutil.parser.isoparse(item["end"]["dateTime"]).replace(tzinfo=datetime.timezone.utc)

# Function to find when a person will next be available
def next_free(schedule, given_time):
    # New approach based on sorting by end time_string
    items = get_items_sorted_by_end_times(schedule)
    next_free = given_time
    index = 0
    for item in items:
        if (item['status'] == 'busy') or (treat_tentative_as_busy and item['status'] == 'tentative'):
            print("End time: ", parse_end_time(item))
            if parse_start_time(item) <= next_free <= parse_end_time(item):
                print("Time in between start and end, updated next_free to be:", parse_end_time(item))
                next_free = parse_end_time(item)
    return next_free


    # # Dissecting the schedule object
    #
    # # Want to deal with everything in UTC, so convert given time - need to test on actual values
    # given_time_UTC = given_time.astimezone(datetime.timezone.utc) # Need to figure out how to have this asright timezone
    # schedules = schedule["value"]
    # details = schedules[0]
    # items = details["scheduleItems"]
    # free_during = False
    # # Create timeline object till the end of the current (or next) working day, and report how long until enext freee time
    # if is_sorted(items):
    #     index = 0
    #     boundary = len(items) - 1
    #     while (index < boundary):
    #         print("First event end time", dateutil.parser.isoparse(items[index]['end']['dateTime']))
    #         print("Second event start time",dateutil.parser.isoparse(items[index + 1]['start']['dateTime']))
    #         print("Is start after end?",(dateutil.parser.isoparse(items[index]['end']['dateTime']) < dateutil.parser.isoparse(items[index + 1]['start']['dateTime'])))
    #         if (dateutil.parser.isoparse(items[index]['end']['dateTime']) < dateutil.parser.isoparse(items[index + 1]['start']['dateTime'])):
    #             next_free = dateutil.parser.isoparse(items[index]['end']['dateTime'])
    #             print("Is that end in working hours?", (is_in_working_hours(schedule,next_free)))
    #             if(is_in_working_hours(schedule,next_free)):
    #                 free_until = dateutil.parser.isoparse(items[index+1]['start']['dateTime'])
    #                 if (is_in_working_hours(schedule,free_until)):
    #                     free_for = free_until - next_free
    #                     return {"next_free":next_free, "for_minutes":free_for.seconds/60}
    #
    #         index += 1




def is_sorted(scheduleItems):
    index = 0
    length = len(scheduleItems)
    while (index <= length - 2):
        # Compare the start times of the current item and the next, and see if they're in the right order
        if (dateutil.parser.isoparse(scheduleItems[index]['start']['dateTime']) > dateutil.parser.isoparse(scheduleItems[index+1]['start']['dateTime'])):
            return False
        index += 1
    return True


# def clean_schedule_items(scheduleItems):
#     clean_items = []
#     index = 0
#     boundary = len(sheduleItems) - 1
#     while (index <= boundary):
#         if index == boundary:
#             #Special cause
#             print("Do Something special here")
#         else:
#             if (dateutil.parser.isoparse(scheduleItems[index]['end']['dateTime']) > dateutil.parser.isoparse(scheduleItems[index + 1]['end']['dateTime'])):
#




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
