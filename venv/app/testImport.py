import getSchedule
import json
import datetime

schedulestring = '''{
    "@odata.context": "https://graph.microsoft.com/beta/$metadata#Collection(microsoft.graph.scheduleInformation)",
    "value": [
        {
            "scheduleId": "Graham.Allen@uts.edu.au",
            "availabilityView": "2",
            "scheduleItems": [
                {
                    "status": "busy",
                    "start": {
                        "dateTime": "2019-01-23T03:00:00.0000000",
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": "2019-01-23T04:00:00.0000000",
                        "timeZone": "UTC"
                    }
                }
            ],
            "workingHours": {
                "daysOfWeek": [
                    "monday",
                    "tuesday",
                    "thursday",
                    "wednesday",
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
}'''
schedule = json.loads(schedulestring)
for k, v in schedule.items():
    print(str(k))
    print(str(v))


print(getSchedule.isBusy(schedule, datetime.datetime(2019, 1, 24, 6, 30, 0)))

print(str(getSchedule.parse_working_hours_time("08:00:00.0000000","AUS Eastern Standard Time")))
