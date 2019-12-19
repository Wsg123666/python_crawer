from src.eams_crawler.lib.OA import Card, OASession
import src.eams_crawler.exception.exceptions as exception


class StuCard:
    def __init__(self, username, password, begin_date, end_date):
        self.session = OASession(username, password)
        self.begin = begin_date
        self.end = end_date

    def transaction(self):
        if self.session.login():   # OA系统密码正确，成功登入
            card_session = self.session.raw_session()
            card = Card(card_session, self.begin, self.end)
            transactions = card.transaction()
            return transactions

        else:   # OA密码错误
            raise exception.CrawlerException("ce3")

