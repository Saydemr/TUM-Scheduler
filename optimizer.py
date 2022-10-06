import json
import random

allocated_time_slots = []
allocated_schedule = []

def convert_time_indexing(day, hour):
    return day * 24 + hour + 8


def collision(start_time, end_time):
    for time_slot in allocated_time_slots:
        if (start_time >= time_slot[0] and start_time < time_slot[1]) or (end_time > time_slot[0] and end_time <= time_slot[1]) \
                or (start_time <= time_slot[0] and end_time >= time_slot[1]):
            return True
    
    return False

crns = []
data = json.load(open('data-v31.min.json'))

sections = []
for course in data['courses']:
    for classes in course['classes']:
        for section in classes['sections']:
            sections.append(section)
            crns.append(section['crn'])

print("Crns: ", crns)
random.shuffle(crns)


for crn in crns:
    for section in sections:
        if section['crn'] == crn:
            # add the course to the schedule
            temp_schedule = []
            temp_course_crn = []
            
            hasCollision = False
            for schedule in section['schedule']:
                start_time = convert_time_indexing(schedule['day'], schedule['start'])
                end_time = convert_time_indexing(schedule['day'], schedule['start'] + schedule['duration'])
                currentCollision = collision(start_time, end_time)
                if not currentCollision:
                    temp_schedule.append((start_time, end_time))
                    temp_course_crn.append(section['crn'])
                else:
                    hasCollision = True
                
            if not hasCollision:
                allocated_time_slots.extend(temp_schedule)
                allocated_schedule.append(temp_course_crn)


print(allocated_time_slots)
print(sorted(allocated_schedule))
