'''
获取近三年所有今年开课课程的信息汇总
获取近三年每学期今年开课的课程详情
'''
from EAMS import EAMSSession
from lxml import etree
import re
import math
import csv
import xlrd

class Anlysis_Score:
    def __init__(self):
        eams_session = EAMSSession("1432", "010022")
        eams_session.login()
        self.session = eams_session.get_session()
        self.anlysis_data = {}
        self.newfirstTimes = True
        self.totalfirstTimes = True
        self.local_data = {}
        # self.total_data = []

    def get_url_content(self,url,lessionid=662,page_num=1,**kwargs):
        data={
            "pageNo": page_num,
            "lesson.semester.id": lessionid
        }
        if len(kwargs)>0:
            data = dict(data,**kwargs)
        html = self.session.post(url,data=data)

        return html.content.decode("utf-8")

    def get_threeyear_lession(self):
        lession_url ="https://jx.sspu.edu.cn/eams/teach/grade/lesson/report!search.action"
        lession_id = {
            "2019-2020学年秋季学期":662,
            "2019-2020学年春季学期":682,
            "2018-2019春季学期":622,
            "2018-2019夏季学期":642,
            "2018-2019秋季学期":602,
            "2017-2018春季学期":562,
            "2017-2018夏季学期":582,
            "2017-2018秋季学期":561
        }

        for key in lession_id:

            html = self.get_url_content(lession_url,lession_id[key])
            pag_all = re.findall(r"pageInfo(.*?);", html)

            if pag_all:
                page_num = math.ceil(float(re.match(".*,(\d*)\)$", pag_all[0]).group(1)) / 20)

            for page in range(1,page_num+1):
                html = self.get_url_content(lession_url,lession_id[key],page)
                html = etree.HTML(html)
                grid_total = html.xpath("//tbody[contains(@id,'data')]/tr")

                for a_grid in grid_total:
                    selectid = a_grid.xpath(".//*[@name='lesson.id']/@value")[0]
                    lessioncode = a_grid.xpath(".//td[3]//text()")[0]
                    lessionname = "".join(a_grid.xpath(".//td[8]//text()"))
                    coursekey = "{}_{}".format(lessioncode,lessionname)
                    lessionnum = a_grid.xpath(".//a[@title='查看课程安排']/text()")[0]
                    forcast_people = a_grid.xpath(".//a[@title='查看点名册']/text()")[0]
                    self.anlysis_data.setdefault(coursekey, []).append(selectid)
                    self.anlysis_data.setdefault(coursekey,[]).append(forcast_people)
                    self.anlysis_data.setdefault(coursekey, []).append(lession_id[key])
            print(key+"完成获取")

    def hand_code_anlysis(self,code,data):
        report_url = "https://jx.sspu.edu.cn/eams/teach/grade/lesson/report!stat.action"
        html = self.get_url_content(report_url,**data)
        html = etree.HTML(html)
        course_name = "".join(html.xpath("//table[@class='gridtable'][1]/tr")[-1].xpath("./td/text()"))
        try:
            course_name = re.findall("课程名称:(.*)课程",course_name)[0]
        except:
            course_name = re.findall(".*:(.*)C.*:.*",course_name)[0]
        div_text = html.xpath("//div")[-1].xpath("./text()")[0]
        div_data = re.findall(".*\((\d*).*:(.*)\s.*:(\d*).*:(\d*)",div_text)
        try:
            actual_peopele = div_data[0][0]
            average_score = div_data[0][1]
            max_score = div_data[0][2]
            min_score = div_data[0][3]
        except:
            return False

        tr_data = html.xpath("//table[@class='gridtable'][3]//tbody//tr")

        # print(tr_data)
        nine_ten_data = tr_data[0].xpath(".//td[3]/text()")[0]
        eight_night_data = tr_data[1].xpath(".//td[3]/text()")[0]
        seven_eight_data = tr_data[2].xpath(".//td[3]/text()")[0]
        six_seven_data = tr_data[3].xpath(".//td[3]/text()")[0]
        zero_six_data = tr_data[4].xpath(".//td[3]/text()")[0]
        code = code.split("_")

        save_key = {
            "学期id":"*",
            "新学期课程序号":"*",
            "课程代码": code[0],
            "课程教师":code[1],
            "课程名称": course_name,
            "平均分":average_score,
            "最高分":max_score,
            "最低分":min_score,
            "预测人数":'*',
            "实际人数":actual_peopele,
            "90-100比例":nine_ten_data,
            "80-89.9比例":eight_night_data,
            "70-79.9比例":seven_eight_data,
            "60-69.9比例":six_seven_data,
            "0-59.9比例":zero_six_data
        }

        return save_key

    def get_new_average(self,aver_data,key):
        alread_aver_data=0
        for data in aver_data:
            if "%" in data[key]:
                alread_aver_data += float(data[key][:-1])
            else:
                alread_aver_data += float(data[key])

        return round(alread_aver_data/(len(aver_data)),2)

    def get_new_course(self):
        xls_file = xlrd.open_workbook("排课结果.xls")
        xls_sheet = xls_file.sheet_by_index(0)
        num = 1
        while True:
            try:
                list_xls = xls_sheet.row_values(num)
            except:
                break
            list_num = str(list_xls[0])

            list_code = list_xls[2]+"_"+list_xls[4]
            self.local_data.setdefault(list_num,list_code)
            num+=1

    def save_dict_content(self, dic_file,filename,filetitle,*args):
        with open(filename, 'a+', newline="") as csvfile:  # 保存用户信息
            fieldnames = filetitle
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if self.newfirstTimes and args[0] == "new":
                writer.writeheader()
                self.newfirstTimes = False
            elif self.totalfirstTimes and args[0]=="total":
                writer.writeheader()
                self.totalfirstTimes = False
            writer.writerow(dic_file)

    def check_new_course(self,a_data):
        for lcode,lvalue in self.local_data.items():
            if lvalue == a_data:
                return lcode
        return None

    def get_score_anlysis(self):
        data = {
            "scoreSegmentsLength":"5",
            "segStat.scoreSegments[0].min":"0",
            "segStat.scoreSegments[0].max":"59.9",
            "segStat.scoreSegments[1].min":"60",
            "segStat.scoreSegments[1].max":"69.9",
            "segStat.scoreSegments[2].min":"70",
            "segStat.scoreSegments[2].max":"79.9",
            "segStat.scoreSegments[3].min":"80",
            "segStat.scoreSegments[3].max":"89.9",
            "segStat.scoreSegments[4].min":"90",
            "segStat.scoreSegments[4].max":"100",
            "lesson.semester.id":None,
            "lesson.ids":"135687",
            "pageNo":None,
            "kind":"task"
        }
        self.get_new_course()
        newfiletitle = ["新学期序号", "课程代码", "课程名称","课程教师",
                          "平均分均值", "最高分均值", "最低分均值", "预测人数均值", "实际人数均值",
                          "90-100比例均值","80-89.9比例均值",
                          "70-79.9比例均值","60-69.9比例均值","0-59.9比例均值"
                          ]
        totalfiletitle = [
            "学期id",
            "新学期课程序号",
            "课程代码",
            "课程名称",
            "课程教师",
            "平均分",
            "最高分",
            "最低分",
            "预测人数",
            "实际人数",
            "90-100比例",
            "80-89.9比例",
            "70-79.9比例",
            "60-69.9比例",
            "0-59.9比例"]
        # print(len(self.anlysis_data))
        for code,value in self.anlysis_data.items():
            aver_data = []
            fore_cast_people = []
            total_code = []
            for v in value:
                if value.index(v) % 3 ==0:
                    data["lesson.ids"] = v
                    mi_data = self.hand_code_anlysis(code,data)
                    if mi_data!=False:
                        aver_data.append(mi_data)
                        total_code.append(v)
                        # self.total_data.append(mi_data)
                    else:
                        continue
                else:
                    if mi_data and value.index(v) % 3 ==1:
                        fore_cast_people.append(v)
                        mi_data["预测人数"]= v
                    elif mi_data:
                        mi_data["学期id"] = v

            total_code.sort(reverse=True)

            new_fore_cast_people = 0
            for forpeople in fore_cast_people:
                new_fore_cast_people += float(forpeople)
            if len(fore_cast_people)>0:
                new_fore_cast_people = round(new_fore_cast_people / len(fore_cast_people),2)
            # else:
            #     print(str(new_fore_cast_people)+""+str(len(fore_cast_people))+str(code)+""+str(value))
            if len(aver_data)<=0:
                continue
            new_save_data = {
                "新学期序号":"*",
                "课程代码": aver_data[0]["课程代码"],
                "课程名称": aver_data[0]["课程名称"],
                "课程教师": aver_data[0]["课程教师"],
                "平均分均值":self.get_new_average(aver_data,"平均分"),
                "最高分均值": self.get_new_average(aver_data, "最高分"),
                "最低分均值": self.get_new_average(aver_data, "最低分"),
                "预测人数均值":new_fore_cast_people,
                "实际人数均值": self.get_new_average(aver_data, "实际人数"),
                "90-100比例均值": str(self.get_new_average(aver_data, "90-100比例"))+"%",
                "80-89.9比例均值": str(self.get_new_average(aver_data, "80-89.9比例"))+"%",
                "70-79.9比例均值": str(self.get_new_average(aver_data, "70-79.9比例"))+"%",
                "60-69.9比例均值": str(self.get_new_average(aver_data, "60-69.9比例"))+"%",
                "0-59.9比例均值": str(self.get_new_average(aver_data, "0-59.9比例"))+"%",
            }
            lcode = self.check_new_course(code)
            if lcode:
                for total_m in aver_data:
                    total_m["新学期课程序号"] = str(lcode)+"\t"
                    self.save_dict_content(total_m,"(详细)总表.csv",totalfiletitle,"total")
                new_save_data["新学期序号"] = str(lcode)+"\t"
                self.save_dict_content(new_save_data,"(新学期选课)成绩分段统计表.csv",newfiletitle,"new")
                print("完成"+code)
        print("保存完成")

if __name__ == '__main__':
    b = Anlysis_Score()
    b.get_threeyear_lession()
    b.get_score_anlysis()
