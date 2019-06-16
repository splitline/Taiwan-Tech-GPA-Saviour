from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import *
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pprint import pprint
import os
from multiprocessing import Pool
import json
from model import db, GradeData, CourseData
import peewee

DATA_DIR = "/Users/splitline/course-data/1062/"


def get_course_data(pdf_file):
    def get_nth_course(y0):
        if y0 > 370:
            return 0
        if 370 > y0 > 300:
            return 1
        if 300 > y0 > 240:
            return 2
        if 240 > y0 > 180:
            return 3
        if 180 > y0 > 110:
            return 4
        if 110 > y0:
            return 5

    index_x0 = 18.650
    total_x0 = 792.650
    course_name_x0 = 66.650
    grade_coords = [512.150, 554.150, 594.650, 635.900, 676.400, 716.900]  # x0
    grades = [("A+", "A"), ("A-", "B+"), ("B", "B-"),
              ("C+", "C"), ("C-", "D"), ("X", "E")]

    result = []
    fp = open(pdf_file, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            grade_cnts = [0, 0, 0, 0, 0, 0]
            courses = []
            for i, component in enumerate(layout):
                if(isinstance(component, LTTextBoxHorizontal)):
                    text = component.get_text().strip()
                    data = text.split('\n')
                    fixed_x0 = round(component.x0, 3)
                    course_index = get_nth_course(component.y0)
                    if fixed_x0 == course_name_x0:
                        if len(data) == 2:
                            courses.append({
                                "course_no": data[0],
                                "course_name": data[1],
                                "type": 0,
                                "grades": {}
                            })
                        elif len(data) == 1 and len(courses) != 0 and courses[-1]["course_name"] == "":
                            courses[-1]["course_name"] = text
                    if fixed_x0 == index_x0 and " 無 " in text:
                        courses.append({
                            "course_no": text.split(" ")[-1],
                            "course_name": "",
                            "type": 0,
                            "grades": {}
                        })
                    if fixed_x0 in grade_coords:
                        index = grade_coords.index(fixed_x0)
                        for s in data:
                            grade = grades[index][0] if int(
                                grade_cnts[index] % 4) <= 1 else grades[index][1]
                            if course_index >= len(courses):
                                break
                            if s.isdecimal():
                                courses[course_index]["grades"][grade] = int(s)
                                grade_cnts[index] += 1
                            elif s.endswith("%") or s == "--":
                                grade_cnts[index] += 1
                            elif s.endswith("通過"):
                                courses[course_index]["type"] = 1
                                grade_cnts[index] += 1
                    # if fixed_x0 == total_x0 and data[1].isdecimal():
                    #     courses[course_index]["total"] = int(data[1])

            result += courses
    return result


gp_mapping = {"A+": 4.3, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
              "C+": 2.3, "C": 2.0, "C-": 1.7, "D": 1.0, "E": 0.0, "X": 0.0}

data = get_course_data(DATA_DIR+"B10630040.pdf")
print(data)


def process_data(f, i, file_num):
    print(f, "{}/{}".format(i, file_num))
    try:
        data = get_course_data(DATA_DIR + f)
    except IndexError as e:
        print("IndexError", e)
        return
    db.connect(True)
    for d in data:
        d['total'] = sum(d['grades'].values())
        d['GPA'] = sum(map(lambda x: gp_mapping[x[0]] * x[1], d['grades'].items())) / d['total']
        try:
            GradeData.create(semester=DATA_DIR[-5:-1],
                             course_no=d['course_no'],
                             course_name=d['course_name'],
                             grades=json.dumps(d['grades']),
                             total=d['total'],
                             GPA=d['GPA'],
                             type=d['type'])
        except peewee.IntegrityError as e:
            pass
            # print(e)
    db.close()



# if __name__ == "__main__":
#     db.connect()
#     db.create_tables([CourseData, GradeData])
#     db.close()
#     files = os.listdir(DATA_DIR)
#     file_num = len(files)

#     pool = Pool()
#     for i, f in enumerate(files):
#         if f.endswith(".pdf"):
#             pool.apply_async(process_data, args=(f, i, file_num))

#     pool.close()
#     pool.join()
