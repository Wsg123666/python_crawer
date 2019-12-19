from src.eams_crawler.database.connect import Database
from src.eams_crawler.database.insert import insert_from_dic, insert_many_from_dic, insert_ignore_many_from_dic


class UserDao:
    def __init__(self, database_obj):
        self.__table_name = "user"
        self.__db = database_obj

    # def username_exist_add_phone(self, phone_number, country_code, username):
    #     sql = "INSERT INTO user_phone (phone_number, country_code, username) VALUES (%s, %s, %s)"
    #     rs = self.__db.get_cursor().execute(sql, [phone_number, country_code, username])
    #     if rs > 0:
    #         return True
    #     else:
    #         return False

    # def is_phone_number_exist(self, phone_number, country_code):
    #     sql = "SELECT * FROM user_phone WHERE phone_number='"+phone_number+"' AND country_code='"+country_code+"'"
    #     rs = self.__db.execute(sql)
    #     if rs > 0:
    #         return True
    #     else:
    #         return False

    def is_user_exist(self, username):
        sql = "SELECT * FROM "+self.__table_name+" WHERE username='"+username+"'"
        rs = self.__db.execute(sql)
        if rs > 0:
            return True
        else:
            return False

    def add_user(self, username, password, origin):
        sql = ""
        if origin == 0:
            sql = "INSERT INTO "+self.__table_name+" (username,password_oa) VALUES (%s, %s)"
        elif origin == 1:
            sql = "INSERT INTO "+self.__table_name+" (username,password_eams) VALUES (%s, %s)"
        rs1 = self.__db.get_cursor().execute(sql, [username, password])

        # self.__db.commit()
        if rs1 > 0:
            return True
        else:
            return False

    def change_password(self, username, password, origin):
        sql = ""
        if origin == 0:
            sql = "UPDATE " + self.__table_name + " SET password_oa=%s WHERE username=%s"
        elif origin == 1:
            sql = "UPDATE " + self.__table_name + " SET password_eams=%s WHERE username=%s"
        rs = self.__db.get_cursor().execute(sql, [password, username])
        # self.__db.commit()
        if rs > 0:
            return True
        else:
            return False

    def is_password_change(self, username, new_password, origin):
        sql = ""
        if origin == 0:
            sql = "SELECT * FROM " + self.__table_name + " WHERE username=%s and password_oa=%s"
        elif origin == 1:
            sql = "SELECT * FROM " + self.__table_name + " WHERE username=%s and password_eams=%s"
        rs = self.__db.get_cursor().execute(sql, [username, new_password])
        if rs > 0:
            return False
        else:
            return True

# print(UserDao().is_password_change('20171130314', '060031', 0))


class UserDetailDao:
    def __init__(self, database_obj):
        self.__db = database_obj

    def add(self, user_detail_dic):
        return insert_from_dic(self.__db, "user_detail", user_detail_dic)


class UsernameCourseIdDao:
    def __init__(self, database_obj):
        self.__db = database_obj

    def add(self, dic_list):
        return insert_many_from_dic(self.__db, "username_courseid", dic_list)

    def update(self, dic_list, username, semester):
        sql = "DELETE FROM username_courseid WHERE username = %s AND semester=%s"
        self.__db.get_cursor().execute(sql, [username, semester])
        return self.add(dic_list)


class SessionDao:
    def __init__(self, database_obj):
        self.__db = database_obj

    def add(self, session_dic):
        return insert_from_dic(self.__db, "session", session_dic)


class UserGradeSummaryDao:
    def __init__(self, database_obj):
        self.__db = database_obj

    def add(self, dic_list):
        return insert_many_from_dic(self.__db, "semester_grade_summary", dic_list)


