from flask import Flask, Response, render_template, jsonify, request, redirect
from model import db, GradeData, CourseData
from playhouse.shortcuts import model_to_dict

app = Flask(__name__)


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.route('/')
def index():
    ge_top3 = {}
    for dimension in ["A", "B", "C", "D", "E", "F"]:
        ge_top3[dimension] = GradeData.select(GradeData, CourseData).join(CourseData).group_by(GradeData). \
            where(CourseData.dimension == dimension,
                  GradeData.course_no.contains("3T") == False,
                  GradeData.course_no.contains("3N") == False).order_by(GradeData.GPA.desc()).limit(3)
    return render_template("index.html", ge_top3=ge_top3)


@app.route('/query', methods=['GET', 'POST'])
def query():
    data = request.args
    if all([d[1].strip() == "" for d in data.items()]):
        return redirect("/")

    queries = [
        GradeData.course_name.contains(data.get("course_name", "")),
        GradeData.course_no.contains(data.get("course_no", "")),
        CourseData.lecturer.contains(data.get("lecturer", "")),
        GradeData.type != 1
    ]
    if data.get("ntust_only"):
        queries += [GradeData.course_no.contains("3T") == False,
                    GradeData.course_no.contains("3N") == False]
    if data.get("general"):
        queries += [CourseData.dimension != None]
    courses = GradeData.select(GradeData, CourseData).join(CourseData).group_by(
        GradeData).where(*queries).order_by(GradeData.GPA.desc())
    return render_template("query.html", courses=courses)


@app.route('/api/course/<course_no>')
def course_api(course_no):
    data = GradeData.select().join(CourseData).where(
        CourseData.course_no == course_no)
    result = [model_to_dict(d, backrefs=True) for d in data]
    return jsonify(result)


if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
