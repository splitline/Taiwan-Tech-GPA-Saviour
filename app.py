from flask import Flask, Response, render_template, jsonify, request, redirect
from model import db, GradeData, CourseData
from playhouse.shortcuts import model_to_dict
from peewee import fn, SQL

app = Flask(__name__)


def get_grade_data():
    return GradeData.select(GradeData, CourseData).join(CourseData).group_by(GradeData)


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.route('/')
def index():
    ge_dim = ["A", "B", "C", "D", "E", "F"]
    ge_top3 = {}
    for dimension in ge_dim:
        ge_top3[dimension] = get_grade_data().where(
            CourseData.dimension == dimension,
            GradeData.course_no.contains("3T") == False,
            GradeData.course_no.contains("3N") == False).order_by(GradeData.GPA.desc()).limit(3)

    dep_mapping = {"AC": "工程技術研究所自動化及控制學程(自動化及控制研究所)", "FN": "財務金融研究所", "AD": "建築系", "GD": "全球發展工程學士學位學程", "AT": "應用科技學士學位學程", "GE": "人文社會學科", "BA": "企業管理系", "GX": "學士後綠能產業機電工程學士學位學程", "BB": "醫學工程學士學位學程", "HC": "不分系學士班", "BE": "醫學工程研究所", "IB": "(學士後)智慧財產權學士學位學程", "CC": "文學(人文社會學科)外文(語言中心)體育(體育室)[106學年前]", "IM": "工業管理系", "CD": "創意設計學士班", "MA": "MBA", "CE": "工程學士班", "MB": "管理學士班", "CH": "化學工程系", "ME": "機械工程系", "CI": "色彩與照明科技研究所", "MG": "管理研究所", "CS": "資訊工程系", "MI": "資訊管理系", "CT": "營建工程系", "MS": "工程技術研究所材料科技學程(材料科技研究所)",
                   "CX": "色彩影像與照明科技學士學位學程", "PA": "專利研究所", "DE": "設計研究所", "PE": "體育(體育室)", "DT": "工商設計系", "RD": "高階科技研發碩士學位學程", "EC": "電資學士班", "SA": "(學務處服務型通識課程、軍訓課程[104學年前])", "EE": "電機工程系", "SG": "新加坡管理碩士在職專班", "EN": "應用科技研究所(工程技術研究所[100學年度前])", "TB": "科技管理學士學位學程", "EO": "光電工程研究所", "TC": "通識教育中心、軍訓課程[104學年起]", "EP": "師資培育中心", "TE": "先進科技全英語外國學生專班", "ET": "電子工程系", "TM": "科技管理研究所", "FB": "財務金融學士學位學程", "TX": "材料科學與工程系(高分子工程系[99學年前])", "FE": "語言中心", "VE": "數位學習與教育研究所(技術及職業教育研究所[99學年前])", "FL": "應用外語系"}

    dep_gpa = []
    for key in dep_mapping:
        query = GradeData.select(fn.AVG(GradeData.GPA).alias('avg'))\
            .where(GradeData.course_no.contains(key))
        if query.exists():
            dep_gpa.append({"no": key,
                            "detail": dep_mapping[key],
                            "gpa": query.get().avg})

    dep_gpa.sort(key=lambda data: data['gpa'], reverse=True)
    return render_template("index.html", ge_top3=ge_top3, ge_dim=ge_dim, dep_gpa=dep_gpa)


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
    courses = get_grade_data().where(*queries).order_by(GradeData.GPA.desc())
    return render_template("query.html", courses=courses)


@app.route('/api/course/<course_no>')
def course_api(course_no):
    data = GradeData.select().join(CourseData).where(
        CourseData.course_no == course_no)
    result = [model_to_dict(d, backrefs=True) for d in data]
    return jsonify(result)


if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
