import bs4
from app import *
from src.eams_crawler.lib.EAMS import *

class Application:
    def __init__(self,strenv):
        self.env_list = strenv.split(";")

    def hand_env(self):
        for env in self.env_list:
            func,content = env.split(":")
            content_list = content.split(",")
            if func == "sport":
                func = sport_morning_run
                self.application(func,content_list)
            elif func=="course":
                func = course_update
                self.application(func, content_list)
            elif func=="card":
                func = card_transaction
                self.application(func,content_list)
            elif func=="stuid":
                self.application(func,content_list)
            elif func=="user_detail":
                self.application(func,content_list)
            elif func=="all_semester_summary":
                self.application(func,content_list)
            elif func=="photo":
                self.application(func,content_list)
            elif func=="course_another_way":
                func=EAMSParser
                self.application(func, content_list)


    def eams_login(self,par_list):
        try:
            if par_list["system"] == "0":
                oa_session = OA.OASession(par_list["username"], par_list["password"])
                if oa_session.login():
                    eams_parser = EAMSParser(oa_session)
            elif par_list["system"] == "1":
                eams_session = EAMS.EAMSSession(par_list["username"], par_list["password"])
                if eams_session.login():
                    eams_parser = EAMSParser(eams_session)
                else:
                    raise exceptions.CrawlerException("ce4")

            return eams_parser

        except Exception as e:
            if "system" in str(e):
                raise exceptions.CrawlerException("系统没有选对")

    def application(self,func,content_list):
        par_list = {content_list[m*2]:content_list[m*2+1] for m in range(int(len(content_list)/2))}
        # print(par_list)
        if func==sport_morning_run:
            try:#sport:username,20181130340,password,wsg440295.
                sport = func(par_list["username"],par_list["password"])
                print("运行sport")
                print(sport)
            except Exception as e:
                print(e)

        elif func==course_update:
            try:#course:username,20181130340,password,123378,system,1,stuid,250543,semester,662"
                course = func(par_list["username"],par_list["password"],par_list["system"],par_list["stuid"],par_list["semester"])
                print("运行course")
                print(course)
            except Exception as e:
                print(e)

        elif func==card_transaction:
            try:#card:username,password,begin_date,"",end_date,""
                card = card_transaction(par_list["username"],par_list["password"],par_list["begin_data"],par_list["end_date"])
                print("运行card")
                print(card)
            except Exception as e:
                print(e)

        elif func=="stuid":
            try:
                eams_parser = self.eams_login(par_list)
                result = eams_parser.get_stuid()
                print(result)

            except Exception as e:
                print(e)

        elif func=="user_detail":
            try:
                eams_parser = self.eams_login(par_list)
                result = eams_parser.get_user_detail()
                print(result)
            except Exception as e:
                print(e)

        elif func=="all_semester_summary":
            try:
                eams_parser = self.eams_login(par_list)
                result = eams_parser.get_all_semester_summary()
                print(result)
            except Exception as e:
                print(e)

        elif func=="photo":
            try:
                eams_parser = self.eams_login(par_list)
                result = eams_parser.save_photo()
                print(result)
            except Exception as e:
                print(e)

        elif func==EAMSParser:
            try:
                eams_parser = self.eams_login(par_list)
                result = eams_parser.get_course_table_another_way()
                print(result)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    stringq = "sport:username,20181130340,password,wsg440295.;course:username,20181130340,password,123378,system,1,stuid,250543,semester,662"
    app = Application("course_another_way:username,20181130340,password,wsg440295.")
    app.hand_env()

