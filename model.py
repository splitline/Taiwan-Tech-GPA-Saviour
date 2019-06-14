from peewee import *

db = SqliteDatabase('course.db', check_same_thread=True)


class BaseModel(Model):
    class Meta:
        database = db

class GradeData(BaseModel):
    semester = CharField(4)
    course_no = TextField()
    course_name = TextField()
    grades = TextField()
    total = IntegerField()
    type = BooleanField()
    GPA = DoubleField()

    class Meta:
        indexes = (
            (('semester', 'course_no'), True),
        )

class CourseData(BaseModel):
    semester = CharField(4)
    course_no = TextField()
    course_name = TextField()
    credit = DoubleField()
    node = TextField(null=True)
    dimension = CharField(1, null=True)
    lecturer = TextField(null=True)
    grade_data = ForeignKeyField(GradeData, backref='course_data', null=True, default=None)
    class Meta:
        indexes = (
            (('semester', 'course_no'), True),
        )
