from src.eams_crawler.lib.OA import OASession
from src.eams_crawler.lib.EAMS import EAMSSession, EAMSParser
import src.eams_crawler.database.dao as dao
from src.eams_crawler.database.connect import Database
from src.eams_crawler.exception import exceptions


class Login:
    def __init__(self, username, password):
        self.__username = username
        self.__password = password

        self.__eams_parser = None
        self.db = Database()

    def __which_way_login(self):  # oa：0, eams: 1, error: -1
        oa_session = OASession(username=self.__username, password=self.__password)
        if oa_session.login():
            self.__eams_parser = EAMSParser(oa_session)
            return 0
        else:
            eams_session = EAMSSession(username=self.__username, password=self.__password)
            if eams_session.login():
                self.__eams_parser = EAMSParser(eams_session)
                return 1
            else:
                raise exceptions.CrawlerException("ce1")

    def __login_state(self):
        userdao = dao.UserDao(self.db)
        way = self.__which_way_login()
        if userdao.is_user_exist(self.__username):  # user exist
            if userdao.is_password_change(self.__username, self.__password, way):
                userdao.change_password(self.__username, self.__password, way)
            return 1  # change user's password successfully, old user

        else:  # new user
            if userdao.add_user(self.__username, self.__password, way):
                return 2  # "add successfully, and new user"
            else:
                raise exceptions.DatabaseException("de1")  # "pw&un right, but db add failed"

    def __save_user_detail(self):
        userdetaildao = dao.UserDetailDao(self.db)
        dic = self.__eams_parser.get_user_detail()
        return userdetaildao.add(dic)

    def __save_user_course_table(self):
        # dic = self.__eams_parser.get_course_table()
        dic = self.__eams_parser.get_course_table_another_way()
        if dic is not None:
            usernameCourseIdDao = dao.UsernameCourseIdDao(self.db)
            return usernameCourseIdDao.add(dic)
        else:
            return 1

    def __save_user_grade_summary(self):
        userGradeSummaryDao = dao.UserGradeSummaryDao(self.db)
        dic_list = self.__eams_parser.get_all_semester_summary()
        return userGradeSummaryDao.add(dic_list)

    def log(self):
        log_state = self.__login_state()

        if log_state == 1:
            return 1  # old user

        elif log_state == 2:   # 新用户，且登录成功
            crawler_state = 0

            if not self.__save_user_detail():  # 保存用户个人信息
                raise exceptions.DatabaseException("de2")

            if not self.__save_user_course_table():  # 保存用户课表
                raise exceptions.DatabaseException("de3")

            if not self.__save_user_grade_summary():   # 保存用户成绩summery
                raise exceptions.DatabaseException("de4")

            return crawler_state




