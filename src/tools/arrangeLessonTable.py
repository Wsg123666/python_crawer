from src.eams_crawler.database.connect import Database
import src.eams_crawler.database.insert as insert
import re

# au_2019_2020  to  au_2019_2020_simple


def range2days(string, mode):   # 全周:0, 单周:1, 双周:2
    begin, end = string.split("-")
    new_str = ""
    if mode == 0:
        for i in range(int(begin), int(end)+1):
            new_str = new_str+str(i)+","
    elif mode == 2:
        for i in range(int(begin), int(end)+1):
            if i%2 == 0:
                new_str = new_str+str(i)+","
    elif mode == 1:
        for i in range(int(begin), int(end)+1):
            if i%2 != 0:
                new_str = new_str+str(i)+","

    return new_str


database = Database()
sql = "SELECT * FROM 682_course"
num = database.execute(sql)
rs = database.get_cursor().fetchall()

for i in range(num):
    print(i)
    result = rs[i]
    db_course_id = result[0]  # 1
    try:
        for day in range(10, 17):
            class_info = result[day]
            if class_info == '':
                continue
            else:
                db_day = day-9  # 2
                a_str_list = class_info.split(";")   # case: 10-12 节  第[7-11]周 足球场南 ;10-12 节  第[1-6]周 5222
                for a_str in a_str_list:
                    detail_list = a_str.split(" ")
                    db_section = detail_list[0]  # 3
                    db_begin = db_section.split("-")[0]  # 6
                    db_place = detail_list[-2]  # 5
                    week_num_list = re.findall("(?<=\[).*?(?=\])", a_str)
                    for week_num in week_num_list:
                        if "单" in a_str:        # case: 6-7 节  第单[3-15]周 5303
                            db_week = range2days(week_num, 1)  # 4
                        elif "双" in a_str:
                            db_week = range2days(week_num, 2)
                        elif '-' in week_num:
                            db_week = range2days(week_num, 0)
                        else:
                            db_week = week_num

                        # print(db_course_id, db_day, db_section, db_week, db_place)
                        dic = {
                            "course_id": db_course_id,
                            "week": db_week,
                            "day": db_day,
                            "section": db_section,
                            "place": db_place,
                            "begin": db_begin
                        }
                        f = insert.insert_from_dic(database, "682_course_simple", dic)
                        database.commit()
                        if not f:
                            print("########################"+db_course_id+"#############################")

    except Exception as e:
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@"+db_course_id+"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

