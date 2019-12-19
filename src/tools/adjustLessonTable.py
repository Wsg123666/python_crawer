# 调整课程时间工具

# 第5周周3 的课 调整到 第6周周7
# 第5周周3  -> 第7周周7   adjust(5,3,6,7)
# 并不会删除第5周3的课
# 如果想删除第5周周3的课
# adjust(5,3,0,0)

from src.tools.connect import Database
import src.eams_crawler.database.insert as insert


def adjust(from_week, from_day, to_week, to_day):

    database = Database()
    sql = 'SELECT * FROM au_2019_2020_simple WHERE `day`="' + str(from_day) + '" AND FIND_IN_SET("' + str(
        from_week) + '",`week`)'
    num = database.execute(sql)
    rs = database.get_cursor().fetchall()

    if to_week == 0 or to_day == 0:
        print("删除课程模式")
        for i in range(num):
            result = rs[i]
            weeks = str(result[1]).split(",")
            new_weeks = ""
            for week in weeks:
                if week == str(from_week) or week == "":
                    continue
                else:
                    new_weeks = new_weeks+week+","
            sql1 = 'UPDATE au_2019_2020_simple SET week="'+new_weeks+'" WHERE course_id="'+result[0]+'" AND week="'\
                   +result[1]+'" AND day='+str(from_day)+' AND begin='+str(result[3])

            if database.execute(sql1) > 0:
                database.commit()
                print(result[0] + " success!")
            else:
                print("########################" + result[0] + "#############################")

    else:
        # # 更改课程开始
        # print("调整课程模式")
        # for i in range(num):
        #     result = rs[i]
        #     dic = {
        #         "course_id": result[0],
        #         "week": str(to_week),
        #         "day": to_day,
        #         "section": result[4],
        #         "place": result[5],
        #         "begin": result[3]
        #     }
        #
        #     print(dic)
        #     f = insert.insert_from_dic(database, "au_2019_2020_simple", dic)
        #     database.commit()
        #     if not f:
        #         print("########################" + result[0] + "#############################")
        #
        # print("调整课程结束")
        #     # 更改课程结束

        # 更改todo开始
        print("调整todo日期开始")
        database = Database()
        sql = 'SELECT * FROM todo WHERE `week`='+str(from_week)+' AND `day`='+str(from_day)
        num = database.execute(sql)
        rs = database.get_cursor().fetchall()
        for i in range(num):
            result = rs[i]
            update_sql = "UPDATE todo SET `week`="+str(to_week)+", `day`="+str(to_day)+" WHERE todo_id='"+result[0]+"'"
            if database.execute(update_sql) > 0:
                database.commit()
                print(result)
            else:
                print("########################" + result[0] + "#############################")
        # 更改todo结束
        print("调整todo日期结束")

adjust(8, 2, 0, 0)
