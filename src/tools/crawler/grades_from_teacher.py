from src.eams_crawler.lib.EAMS import EAMSSession
from src.eams_crawler.exception import exceptions
from bs4 import BeautifulSoup
import re
import csv
import datetime


# 经济与管理学院: 27
# 国际交流学院（外国留学生事务办公室）: 31
# 工程训练中心: 32
# 体育部: 33
# 应用艺术设计学院: 34
# 文理学部: 491
# 工学部: 476
# 高等职业技术（国际）学院: 473
department = "27"

# 电子商务*: 1311
major = "1311"

# 学期：
# 662：2019-2020秋
# 602：2018-2019秋  ok
# 622：2018-2019春
# 642：2018-2019夏


class Grade:
    def __init__(self, write_user_header, write_score_header):   # write_header: 1(写入header，新文件), 0（不写入）
        eams_session = EAMSSession("1432", "010022")
        eams_session.login()
        self.session = eams_session.get_session()
        self.write_user_header = write_user_header
        self.write_score_header = write_score_header
        self.loop_time = 0
        self.error = 0
        self.success = 0

    # 每学期一个专业所有学生的各科成绩
    def every_student_grade_of_semester(self, semester_id, department_id, major_id, page_no):
        self.loop_time += 1
        url = "https://jx.sspu.edu.cn/eams/teach/grade/course/term-report!stdList.action"
        data = {
            "semester.id": semester_id,
            "orderBy": "std.code",
            "std.project.id": 1,
            "std.department.id": department_id,
            "std.major.id": major_id,
            "stdActive": 1,
            "pageNo": page_no
        }
        page = self.session.post(url=url, data=data)
        soup = BeautifulSoup(page.text, "html.parser")
        tbodys = soup.find_all("tbody")[0]
        tds = tbodys.find_all("td")

        if len(tds) == 0:   # 这一页没有数据了
            print("out of page range")
            exit(0)
        else:   # 这一页有数据
            # 见 term-report.html
            for td_num in range(int(len(tds)/9)):  # 9个一组
                stu_id = tds[td_num*9+0]
                stu_num = tds[td_num*9+1]
                sex = tds[td_num*9+3]
                grade = tds[td_num*9+4]
                classs = tds[td_num*9+7]

                stu_id = stu_id.find_all("input")[0]['value']    # 学生编号
                stu_num = stu_num.find_all("a")[0].text    # 学号
                sex = sex.text    # 性别
                grade = grade.text    # 年级年份  2015-9
                classs = classs.text   # 班级


                # 获取学生详情
                # 见 chengjidan.html
                url1 = "https://jx.sspu.edu.cn/eams/teach/grade/course/term-report!report.action"
                data = {
                    "semester.id": semester_id,
                    "std.ids": stu_id
                }
                stu_page = self.session.post(url1, data)
                soup = BeautifulSoup(stu_page.text, "html.parser")
                table = soup.find_all("table")[0]

                divs = table.find_all("div")
                table_name = divs[0].find_all("strong")[0].text   # 成绩单名称
                semester = divs[1].text    # 学期名称
                user_detail = divs[2].text
                all_scores = divs[3].text

                user_detail = str(user_detail).split("\n")
                user_department = user_detail[0].split(":")[1]    # 学院
                user_major = user_detail[1].split(":")[1]   # 专业
                user_stu_number = user_detail[2].split(":")[1]   # 学号
                user_name = user_detail[3].split("：")[1]    # 学生姓名

                all_scores = str(all_scores).split("\n")
                user_xuanxiu_score = all_scores[0].split(":")[1].strip()   # 选修学分 .strip() 去空格
                user_shixiu_score = all_scores[1].split(":")[1].strip()   # 实修学分
                user_pingjun_jidian = all_scores[2].split(":")[1].strip()   # 平均绩点
                user_jiangli_score = all_scores[3].split(":")[1].strip()   # 奖励学分

                score_tr = table.find_all("tr")

                if user_stu_number == stu_num:
                    print("学号符合: "+user_stu_number+", 编号: "+stu_id+", 姓名:"+user_name+", 专业: "+user_major, ", 班级: "+classs, " 有课程: "+str(len(score_tr)-3))

                    with open('datasets/'+str(semester_id)+"_"+str(department_id)+"_"+str(major_id)+'_user.csv', 'a+', newline="") as csvfile:  # 保存用户信息
                        fieldnames = ['成绩单名称', '学期id', "学期名称", "学生id", "学号", "姓名", "性别", "年级", "班级",
                                      "院系", "专业", "选修学分", "实修学分", "平均绩点", "奖励学分"]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        if self.write_user_header == 1 and self.loop_time == 1 and td_num == 0:   # 让写头部，且第一次循环才写头
                            writer.writeheader()
                        user_dic = {
                            "成绩单名称": str(table_name),
                            "学期id": str(semester_id),
                            "学期名称": str(semester),
                            "学生id": str(stu_id),
                            "学号": str(stu_num),
                            "姓名": str(user_name),
                            "性别": str(sex),
                            "年级": str(grade),
                            "班级": str(classs),
                            "院系": str(user_department),
                            "专业": str(user_major),
                            "选修学分": str(user_shixiu_score),
                            "实修学分": str(user_xuanxiu_score),
                            "平均绩点": str(user_pingjun_jidian),
                            "奖励学分": str(user_jiangli_score)
                        }
                        writer.writerow(user_dic)
                        print("保存学号 "+stu_num+" 用户信息成功")

                    if len(score_tr) > 3:  # 该学生本学期有成绩
                        for num in range(2, len(score_tr) - 1):
                            inner_tds = score_tr[num].find_all("td")
                            class_name = inner_tds[0].text   # 课程名称
                            xuefen = inner_tds[1].text   # 学分
                            xingzhi = inner_tds[2].text   # 性质
                            chengji = inner_tds[3].text.strip()   # 成绩
                            jidian = inner_tds[4].text   # 绩点

                            with open('datasets/' + str(semester_id) + "_" + str(department_id) + "_" + str(
                                    major_id) + '_score.csv', 'a+', newline="") as csvfile:  # 保存成绩信息
                                fieldnames = ['学期id', '学生id', "学号", "课程名称", "学分", "性质", "成绩", "绩点"]
                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                if self.write_score_header == 1 and self.loop_time == 1 and td_num == 0 and num == 2:  # 让写头部，且第一次循环才写头
                                    writer.writeheader()
                                user_dic = {
                                    "学期id": str(semester_id),
                                    "学生id": str(stu_id),
                                    "学号": str(stu_num),
                                    "课程名称": str(class_name),
                                    "学分": str(xuefen),
                                    "性质": str(xingzhi),
                                    "成绩": str(chengji),
                                    "绩点": str(jidian)
                                }
                                writer.writerow(user_dic)
                        print("保存学号 " + stu_num + " 用户成绩成功\n")

                else:
                    print("!!!!!!!!!学号不符合: " + user_stu_number + ", 编号: " + stu_id+", 姓名:"+user_name + ", 专业: " + user_major, ", 班级: " + classs,
                          " 有课程: " + str(len(score_tr) - 3))

    # 获取每个学期所有在读学生成绩
    def all_student_grade_of_a_semester(self, semester_id, page_no):
        self.loop_time += 1
        url = "https://jx.sspu.edu.cn/eams/teach/grade/course/term-report!stdList.action"
        data = {
            "semester.id": semester_id,
            "orderBy": "std.code",
            "std.project.id": 1,
            "stdActive": 1,
            "pageNo": page_no
        }
        page = self.session.post(url=url, data=data)
        soup = BeautifulSoup(page.text, "html.parser")
        tbodys = soup.find_all("tbody")[0]
        tds = tbodys.find_all("td")

        if len(tds) == 0:  # 这一页没有数据了
            print("out of page range")
            raise exceptions.CrawlerException("OFPR")
        else:  # 这一页有数据
            # 见 term-report.html
            for td_num in range(int(len(tds) / 9)):  # 9个一组
                stu_id = tds[td_num * 9 + 0]
                stu_num = tds[td_num * 9 + 1]
                sex = tds[td_num * 9 + 3]
                grade = tds[td_num * 9 + 4]
                classs = tds[td_num * 9 + 7]

                stu_id = stu_id.find_all("input")[0]['value']  # 学生编号
                stu_num = stu_num.find_all("a")[0].text  # 学号
                sex = sex.text  # 性别
                grade = grade.text  # 年级年份  2015-9
                classs = classs.text  # 班级

                # 获取学生详情
                url1 = "https://jx.sspu.edu.cn/eams/teach/grade/course/term-report!report.action"
                data = {
                    "semester.id": semester_id,
                    "std.ids": stu_id
                }
                stu_page = self.session.post(url1, data)
                soup = BeautifulSoup(stu_page.text, "html.parser")
                table = soup.find_all("table")[0]

                divs = table.find_all("div")
                table_name = divs[0].find_all("strong")[0].text  # 成绩单名称
                semester = divs[1].text  # 学期名称
                user_detail = divs[2].text
                all_scores = divs[3].text

                user_detail = str(user_detail).split("\n")
                user_department = user_detail[0].split(":")[1]  # 学院
                user_major = user_detail[1].split(":")[1]  # 专业
                user_stu_number = user_detail[2].split(":")[1]  # 学号
                user_name = user_detail[3].split("：")[1]  # 学生姓名

                all_scores = str(all_scores).split("\n")
                user_xuanxiu_score = all_scores[0].split(":")[1].strip()  # 选修学分 .strip() 去空格
                user_shixiu_score = all_scores[1].split(":")[1].strip()  # 实修学分
                user_pingjun_jidian = all_scores[2].split(":")[1].strip()  # 平均绩点
                user_jiangli_score = all_scores[3].split(":")[1].strip()  # 奖励学分

                score_tr = table.find_all("tr")

                if user_stu_number == stu_num:
                    print("学号符合: " + user_stu_number + ", 编号: " + stu_id + ", 姓名:" + user_name + ", 专业: " + user_major,
                          ", 班级: " + classs, " 有课程: " + str(len(score_tr) - 3))

                    with open('datasets/all_students/' + str(semester_id) + '_user.csv', 'a+', newline="") as csvfile:  # 保存用户信息
                        fieldnames = ['成绩单名称', '学期id', "学期名称", "学生id", "学号", "姓名", "性别", "年级", "班级",
                                      "院系", "专业", "选修学分", "实修学分", "平均绩点", "奖励学分"]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        if self.write_user_header == 1 and self.loop_time == 1 and td_num == 0:  # 让写头部，且第一次循环才写头
                            writer.writeheader()
                        user_dic = {
                            "成绩单名称": str(table_name),
                            "学期id": str(semester_id),
                            "学期名称": str(semester),
                            "学生id": str(stu_id),
                            "学号": str(stu_num),
                            "姓名": str(user_name),
                            "性别": str(sex),
                            "年级": str(grade),
                            "班级": str(classs),
                            "院系": str(user_department),
                            "专业": str(user_major),
                            "选修学分": str(user_shixiu_score),
                            "实修学分": str(user_xuanxiu_score),
                            "平均绩点": str(user_pingjun_jidian),
                            "奖励学分": str(user_jiangli_score)
                        }
                        writer.writerow(user_dic)
                        print("保存学号 " + stu_num + " 用户信息成功")

                    if len(score_tr) > 3:  # 该学生本学期有成绩
                        for num in range(2, len(score_tr) - 1):
                            inner_tds = score_tr[num].find_all("td")
                            class_name = inner_tds[0].text  # 课程名称
                            xuefen = inner_tds[1].text  # 学分
                            xingzhi = inner_tds[2].text  # 性质
                            chengji = inner_tds[3].text.strip()  # 成绩
                            jidian = inner_tds[4].text  # 绩点

                            with open('datasets/all_students/' + str(semester_id) + '_score.csv', 'a+', newline="") as csvfile:  # 保存成绩信息
                                fieldnames = ['学期id', '学生id', "学号", "课程名称", "学分", "性质", "成绩", "绩点"]
                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                if self.write_score_header == 1 and self.loop_time == 1 and td_num == 0 and num == 2:  # 让写头部，且第一次循环才写头
                                    writer.writeheader()
                                user_dic = {
                                    "学期id": str(semester_id),
                                    "学生id": str(stu_id),
                                    "学号": str(stu_num),
                                    "课程名称": str(class_name),
                                    "学分": str(xuefen),
                                    "性质": str(xingzhi),
                                    "成绩": str(chengji),
                                    "绩点": str(jidian)
                                }
                                writer.writerow(user_dic)
                        print("保存学号 " + stu_num + " 用户成绩成功\n")
                        self.success += 1

                else:
                    error_text = "!!!!!!!!!学号不符合: " + user_stu_number + ", 编号: " + stu_id + ", 姓名:" + user_name + ", 专业: " + str(user_major) + ", 班级: " + classs + " 有课程: " + str(len(score_tr) - 3)
                    print(error_text)
                    with open("datasets/all_students/error.txt", "a+") as f:
                        f.write(error_text)
                    self.error += 1


class Runner:

    @staticmethod
    def get_each_semester_all_students():

        semesters = [602, 622, 642, 561, 562, 582, 501, 521, 541]

        for sem_num in range(len(semesters)):
            grade = Grade(1, 1)
            begin_time = datetime.datetime.now()   # 开始时间

            for i in range(1, 10000000):
                try:
                    grade.all_student_grade_of_a_semester(semesters[sem_num], i)
                except exceptions.CrawlerException:
                    end_time = datetime.datetime.now()   # 结束时间
                    with open('datasets/all_students/result.csv', 'a+', newline="") as csvfile:  # 保存成绩信息
                        fieldnames = ['学期id', '成功人数', "失败人数", "采集开始时间", "采集结束时间"]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        if sem_num == 0:  # 让写头部，且第一次循环才写头
                            writer.writeheader()
                        user_dic = {
                            "学期id": str(semesters[sem_num]),
                            "成功人数": str(grade.success),
                            "失败人数": str(grade.error),
                            "采集开始时间": str(begin_time),
                            "采集结束时间": str(end_time)
                        }
                        writer.writerow(user_dic)
                    break


Runner.get_each_semester_all_students()

