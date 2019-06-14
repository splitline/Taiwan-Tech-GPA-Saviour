import json
import os
import peewee
from model import db, CourseData, GradeData

JSON_FILE = "/Users/splitline/course-data/1071.json"
data = json.load(open(JSON_FILE))

db.connect()
db.create_tables([CourseData, GradeData])
for course in data:
    try:
        grade_data = GradeData.select().where(
            GradeData.semester == course['Semester'],
            (GradeData.course_no == course['CourseNo']) |
            (GradeData.course_no == course['CourseNo'][:-1])
        )
        CourseData.create(
            semester=course['Semester'],
            course_no=course['CourseNo'],
            course_name=course['CourseName'],
            credit=course['CreditPoint'],
            node=course['Node'],
            dimension=course['Dimension'] if course['Dimension'] != "" and course['Dimension'] != "無" else None,
            lecturer=course['CourseTeacher'],
            grade_data=grade_data.get() if grade_data.exists() else None
        )
    except peewee.IntegrityError as e:
        pass
        # print(course)
        # print(e)

db.close()
