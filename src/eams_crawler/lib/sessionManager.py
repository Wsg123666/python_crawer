from hashlib import sha1
import time
from src.eams_crawler.database.dao import SessionDao


class Session:
    username = ""
    password = ""

    def __init__(self, username, password, db_obj):
        self.username = username
        self.password = password
        self.db = db_obj

    def encode(self):
        key = "qwertyuiop"
        now_time = time.time()
        string = self.username + key + self.password + str(now_time)
        s1 = sha1()
        s1.update(string.encode('utf-8'))
        res = s1.hexdigest()
        return res

    def add(self):
        res = self.encode()
        dic = {
            "sessionid": res,
            "username": self.username
        }
        rs = SessionDao(self.db).add(dic)
        return rs, res
