import pymysql


class Database:   # 得到Database_object

    __username = "root"
    __password = "19990206lyz"
    __address = "cdb-box97608.bj.tencentcdb.com"

    def __init__(self, db='zhishu'):
        self.__database = pymysql.connect(self.__address, self.__username, self.__password, port=10188, charset='utf8', db=db)
        self.__cursor = self.__database.cursor()

    def __del__(self):
        self.__cursor.close()
        self.__database.close()

    def get_cursor(self):
        return self.__cursor

    def get_database(self):
        return self.__database

    def execute(self, sql):
        return self.__cursor.execute(sql)

    def commit(self):
        return self.__database.commit()

    def rollback(self):
        return self.__database.rollback()
