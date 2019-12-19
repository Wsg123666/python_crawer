from src.eams_crawler.lib.OA import SportSystem, OASession
import src.eams_crawler.exception.exceptions as exception
from src.eams_crawler.database.connect import Database
import src.eams_crawler.database.dao as dao


class SportScore:
    def __init__(self, username, password):
        self.oa_session = OASession(username, password)
        self.db = Database()

    def morning_run(self, ):
        if self.oa_session.login():
            sport_session = SportSystem(self.oa_session)
            if sport_session.login_sport_system():
                return sport_session.morning_run()
            else:
                raise exception.CrawlerException("ce8")  # 获取晨跑数据失败

        else:  # OA密码错误
            raise exception.CrawlerException("ce3")


