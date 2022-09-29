from dataclasses import dataclass
import requests
import json

import datetime

def same_week_diff_lectures(date1, date2):
    d1 = datetime.datetime.strptime(date1,'%Y-%m-%dT%H:%M:%S%z')
    d2 = datetime.datetime.strptime(date2,'%Y-%m-%dT%H:%M:%S%z')
    return d1.isocalendar()[1] == d2.isocalendar()[1] \
              and d1.year == d2.year \
                and (d1.weekday() != d2.weekday() \
                or d1.hour != d2.hour \
                )

def same_week(date1, date2):
    d1 = datetime.datetime.strptime(date1,'%Y%m%dT%H%M%SZ')
    d2 = datetime.datetime.strptime(date2,'%Y%m%dT%H%M%SZ')
    return d1.isocalendar()[1] == d2.isocalendar()[1] \
              and d1.year == d2.year

EVENTS_URL = "http://0.0.0.0:80/course/events%3FcourseID%3D"
COURSES_URL = "http://0.0.0.0:80/organization/courses%3FincludeChildren%3Dtrue%26orgUnitID%3D15422"

available_courses = requests.get(COURSES_URL).json()

instructors = []
places = []
courses = []

for course in available_courses:
    courseDTO = {}
    courseDTO["name"] = course["course_name"]["text"]
    courseDTO["code"] = course["course_code"]
    course_id = course["course_id"][-4::]

    try:
        events = requests.get(EVENTS_URL + course["course_id"]).json()
    except:
        continue

    if len(events) == 0:
        continue

    events_in_a_week = []
    events_in_a_week.append(events[0])
    for event in events[1:]:
        if same_week_diff_lectures(event["dtstart"], events[0]["dtstart"]):
            events_in_a_week.append(event)
        else:
            break
    
    events_in_a_week_reversed = []
    events_in_a_week_reversed.append(events[-1])
    for event in events[-2::-1]:
        if same_week_diff_lectures(event["dtstart"], events[-1]["dtstart"]):
            events_in_a_week_reversed.append(event)
        else:
            break

    events = events_in_a_week if len(events_in_a_week) > len(events_in_a_week_reversed) else events_in_a_week_reversed
    
    classes = []
    classDTO = {}
    classDTO["type"] = ""
    
    sectionsDTO = {}
    sections = []
    sectionsDTO["crn"] = course["course_id"]

    schedule = []
    for event in events:
        day = datetime.datetime.strptime(event["dtstart"],'%Y-%m-%dT%H:%M:%S%z').weekday()
        start_hour = datetime.datetime.strptime(event["dtstart"],'%Y-%m-%dT%H:%M:%S%z').hour - 8
        duration = (datetime.datetime.strptime(event["dtend"],'%Y-%m-%dT%H:%M:%S%z') - datetime.datetime.strptime(event["dtstart"],'%Y-%m-%dT%H:%M:%S%z')).seconds // 3600
        place = "Online" if "online" in str(event["address"]["contactName"]).lower() else event["address"]["roomCode"] + " " + event["address"]["roomAdditionalData"]
        if place not in places:
            places.append(place)
            place = len(places) - 1
        else:
            place = places.index(place)
        
        schedule.append({"day": day,
        "place": place,
        "start": start_hour,
        "duration": duration})
    
    sectionsDTO["schedule"] = schedule
    sectionsDTO["group"] = ""
    
    
    instructor = course["contacts"]["person"][0]["name"]["given"] + " " + course["contacts"]["person"][0]["name"]["family"]
    if instructor not in instructors:
        instructors.append(instructor)
        instructor = len(instructors) - 1
    else:
        instructor = instructors.index(instructor)
    
    sectionsDTO["instructors"] = instructor
    sections.append(sectionsDTO)

    classDTO["sections"] = sections
    classes.append(classDTO)

    courseDTO["classes"] = classes
    courses.append(courseDTO)

out = {"courses": courses, "instructors": instructors, "places": places}

json.dump(out, indent=4, fp=open("data-v31.min.json", "w+"))
