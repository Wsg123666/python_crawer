import requests
from bs4 import BeautifulSoup
import random
import src.eams_crawler.exception.exceptions as exception

user_dic = dict()
def hand_sing(username,state,session):
    if len(user_dic)>=2:
        key_list = []
        for dic in user_dic:
           key_list.append(dic)
        for key in key_list:
            if key != username:
                user_dic.pop(key)
    try:
        if state:
            user_dic.setdefault(username,[]).append(state)
            user_dic.setdefault(username,[]).append(session)
        else:
            if user_dic[username]:
                return [True,user_dic[username][1]]

    except Exception as e:
        return [False,""]

class OASession:

    def __init__(self, username, password):
        self.__url = "http://id.sspu.edu.cn/cas/login"
        self.__username = username
        self.__password = password
        self.__session = requests.session()
        self.__session.headers.update({"X-Forwarded-For": "%d.%d.%d.%d" % (
            random.randint(120, 125), random.randint(1, 200), random.randint(1, 200), random.randint(1, 200)),
                                       "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                                       })
        self.__session = requests.session()
    def judge(self):
        def judge_login_in(func):
            def judge_in(self):
                login_in,session = hand_sing(self.__username,False,self.__session)
                if login_in:
                    self.__session = session
                    return True
                if not login_in:
                    print("调用")
                    login_in = func(self)
                    if login_in:
                        hand_sing(self.__username,True,self.__session)
                return login_in
            return judge_in
        return judge_login_in

    @judge("判断是否登录过")
    def login(self):
        main_page = self.__session.get(url=self.__url)
        soup = BeautifulSoup(main_page.text, "html.parser")
        lt = soup.find_all('input')[4]
        lt_code = lt.attrs["value"]

        data = {
            "username": self.__username,
            "password": self.__password,
            "imageCodeName": "",
            "errors": 0,
            "lt": lt_code,
            "_eventId": "submit"
        }

        page = self.__session.post(url=self.__url, data=data)

        if page.status_code == 200:
            if "登录成功" in page.text:
                return True
            else:
                return False
        return False

    def get_session(self):
        self.__session.get(url="http://jx.sspu.edu.cn/eams/home.action")
        self.__session.get(url="http://jx.sspu.edu.cn/eams/home.action")
        return self.__session

    def raw_session(self):
        return self.__session

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password


class Card:
    def __init__(self, card_session, begin_date, end_date):  # begin_date,end_date格式: 2019-09-01
        self.session = card_session
        self.begin = begin_date
        self.end = end_date
        self.url1 = "https://card.sspu.edu.cn"
        self.url2 = "https://card.sspu.edu.cn/c"

    def transaction(self):
        # 重要：要访问两次才嫩得到带JSESSIONID的页面
        # 这个页面会set-cookie，set的cookie为JSESSIONID；也就是这个页面的response cookie为JSESSIONID
        self.session.get(self.url1)

        # 访问这个页面的作用是调用一下刚刚的session，使得response cookie生效
        self.session.get(self.url2)

        url = "https://card.sspu.edu.cn/web/20171130430/1?beginDate=" + self.begin + "&" \
            "p_p_action=0&serialType=1&p_p_mode=view&" \
            "_querydetail_struts_action=%2Fext%2Fecardtransactionquerydetail_result&" \
            "p_p_id=querydetail&p_p_state=maximized&endDate=" + self.end

        html = self.session.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        tbody = soup.find_all("tbody")
        if len(tbody) == 0:   # 没有交易数据
            raise exception.CrawlerException("ce6")
        else:    # 有交易数据
            tran_list = []
            trs = tbody[0].find_all("tr")
            for tr in trs:
                tds = tr.find_all("td")
                tran_dic = {
                    "number": tds[0].text,
                    "entry_datetime": tds[1].text,
                    "happen_datetime": tds[2].text,
                    "place": tds[3].text,
                    "way": tds[4].text,
                    "money": tds[5].text,
                    "balance": tds[6].text
                }
                tran_list.append(tran_dic)
            return tran_list


class SportSystem:
    def __init__(self, OASession):
        self.index_url = "https://tygl.sspu.edu.cn/SportScore/default.aspx"
        self.main_url = "https://tygl.sspu.edu.cn/SportScore/stScore.aspx"
        self.run_url = "https://tygl.sspu.edu.cn/SportScore/stScore.aspx?item=1"
        self.session = OASession.raw_session()
        self.username = OASession.get_username()

    def login_sport_system(self):
        self.session.get(self.index_url)
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": "/wEPDwUKLTM4NjY5Mzc1Ng9kFgJmD2QWCmYPEGRkFgFmZAIBDw8WAh4HVmlzaWJsZWhkZAIDDw8WAh4EVGV4dAW/OiZuYnNwOw0KPHAgY2xhc3M9Ik1zb05vcm1hbCIgc3R5bGU9Ik1BUkdJTi1CT1RUT006IDcuOHB0OyBURVhULUFMSUdOOiBjZW50ZXI7IG1zby1wYXJhLW1hcmdpbi1ib3R0b206IC41Z2QiIGFsaWduPSJjZW50ZXIiPjxzcGFuIHN0eWxlPSJGT05ULVNJWkU6IDE4cHQ7IEZPTlQtRkFNSUxZOiDpu5HkvZMiPjxmb250IGNvbG9yPSIjZmYwMDAwIj7kvZPogrLnrqHnkIbnu7zlkIjmn6Xor6Lns7vnu5/kvb/nlKjor7TmmI48c3BhbiBsYW5nPSJFTi1VUyI+PG86cD48L286cD48L3NwYW4+PC9mb250Pjwvc3Bhbj48L3A+DQo8cCBjbGFzcz0iTXNvTm9ybWFsIiBzdHlsZT0iTUFSR0lOLUxFRlQ6IDE3Ljg1cHQ7IFRFWFQtSU5ERU5UOiAtMTcuODVwdDsgbXNvLWxpc3Q6IGwwIGxldmVsMSBsZm8xOyB0YWItc3RvcHM6IGxpc3QgMTguMHB0Ij48c3BhbiBsYW5nPSJFTi1VUyIgc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgbXNvLWZhcmVhc3QtZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbiI+PHNwYW4gc3R5bGU9Im1zby1saXN0OiBJZ25vcmUiPjEuPHNwYW4gc3R5bGU9IkZPTlQ6IDdwdCBUaW1lcyBOZXcgUm9tYW4iPiZuYnNwOyZuYnNwOyZuYnNwOyZuYnNwOyA8L3NwYW4+PC9zcGFuPjwvc3Bhbj48c3Ryb25nIHN0eWxlPSJtc28tYmlkaS1mb250LXdlaWdodDogbm9ybWFsIj48c3BhbiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTog5a6L5L2TOyBtc28tYXNjaWktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbjsgbXNvLWhhbnNpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW4iPuafpeivoui6q+S7ve+8mjwvc3Bhbj48L3N0cm9uZz48c3BhbiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTog5a6L5L2TOyBtc28tYXNjaWktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbjsgbXNvLWhhbnNpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW4iPuWtpueUn+S4uuacrOS6uuWtpuWPtyjkvovvvJoyMDE4MTExMTQwNSnjgIHkvZPogrLmlZnluIjkuLrmnKzkurrlt6Xlj7fvvIjlkI48L3NwYW4+PHNwYW4gbGFuZz0iRU4tVVMiIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQiPjQ8L3NwYW4+PHNwYW4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6IOWui+S9kzsgbXNvLWFzY2lpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW47IG1zby1oYW5zaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuIj7kvY3vvInjgIHovoXlr7zlkZjkuLrmnKzlrabpmaLnvJblj7fvvIzlkITlrabpmaLnvJblj7flj6booYzpgJrnn6XvvJs8L3NwYW4+PHNwYW4gbGFuZz0iRU4tVVMiIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQiPjxvOnA+PC9vOnA+PC9zcGFuPjwvcD4NCjxwIGNsYXNzPSJNc29Ob3JtYWwiIHN0eWxlPSJNQVJHSU4tTEVGVDogMTcuODVwdDsgVEVYVC1JTkRFTlQ6IC0xNy44NXB0OyBtc28tbGlzdDogbDAgbGV2ZWwxIGxmbzE7IHRhYi1zdG9wczogbGlzdCAxOC4wcHQiPjxzcGFuIGxhbmc9IkVOLVVTIiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBtc28tZmFyZWFzdC1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuIj48c3BhbiBzdHlsZT0ibXNvLWxpc3Q6IElnbm9yZSI+Mi48c3BhbiBzdHlsZT0iRk9OVDogN3B0IFRpbWVzIE5ldyBSb21hbiI+Jm5ic3A7Jm5ic3A7Jm5ic3A7Jm5ic3A7IDwvc3Bhbj48L3NwYW4+PC9zcGFuPjxzdHJvbmcgc3R5bGU9Im1zby1iaWRpLWZvbnQtd2VpZ2h0OiBub3JtYWwiPjxzcGFuIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiDlrovkvZM7IG1zby1hc2NpaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuOyBtc28taGFuc2ktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbiI+5p+l6K+i5a+G56CB77yaPC9zcGFuPjwvc3Ryb25nPjxzcGFuIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiDlrovkvZM7IG1zby1hc2NpaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuOyBtc28taGFuc2ktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbiI+5Yid5aeL5a+G56CB77ya5a2m55Sf5Li65pys5Lq65Ye655Sf5pel5pyf44CC5L6L77ya77yIMTk5ODAyMDXvvInjgILkvZPogrLmlZnluIjlkIzmnKzkurrkvZPogrLnrqHnkIbova/ku7blr4bnoIE8L3NwYW4+PHNwYW4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6IOWui+S9kzsgbXNvLWFzY2lpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW47IG1zby1oYW5zaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuIj7jgIHlrabpmaLovoXlr7zlkZjnmbvpmYblr4bnoIHkuLo8L3NwYW4+PHNwYW4gbGFuZz0iRU4tVVMiIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQiPjAwMDAwMDwvc3Bhbj48c3BhbiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTog5a6L5L2TOyBtc28tYXNjaWktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbjsgbXNvLWhhbnNpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW4iPu+8jOmmluasoeeZu+mZhuWQjuivt+WNs+WIu+S/ruaUueacrOS6uuWvhuegge+8jOW5tuWmpeWWhOS/neeuoe+8jOWmguWvhueggemBl+W/mOivt+S4juS9k+iCsumDqOaVmeWtpueuoeeQhue7hDxzdDE6cGVyc29ubmFtZSB3OnN0PSJvbiIgcHJvZHVjdGlkPSLkuIHmtbfojaMiPuS4gea1t+iNozwvc3QxOnBlcnNvbm5hbWU+6ICB5biI6IGU57O777yM6IGU57O755S16K+d77yaPC9zcGFuPjxzcGFuIGxhbmc9IkVOLVVTIiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0Ij41MDIxMTM4OTwvc3Bhbj48c3BhbiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTog5a6L5L2TOyBtc28tYXNjaWktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbjsgbXNvLWhhbnNpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW4iPu+8mzwvc3Bhbj48c3BhbiBsYW5nPSJFTi1VUyIgc3R5bGU9IkZPTlQtU0laRTogMTRwdCI+PG86cD48L286cD48L3NwYW4+PC9wPg0KPHAgY2xhc3M9Ik1zb05vcm1hbCIgc3R5bGU9Ik1BUkdJTi1MRUZUOiAxNy44NXB0OyBURVhULUlOREVOVDogLTE3Ljg1cHQ7IG1zby1saXN0OiBsMCBsZXZlbDEgbGZvMTsgdGFiLXN0b3BzOiBsaXN0IDE4LjBwdCI+PHNwYW4gbGFuZz0iRU4tVVMiIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IG1zby1mYXJlYXN0LWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW4iPjxzcGFuIHN0eWxlPSJtc28tbGlzdDogSWdub3JlIj4zLjxzcGFuIHN0eWxlPSJGT05UOiA3cHQgVGltZXMgTmV3IFJvbWFuIj4mbmJzcDsmbmJzcDsmbmJzcDsmbmJzcDsgPC9zcGFuPjwvc3Bhbj48L3NwYW4+PHN0cm9uZyBzdHlsZT0ibXNvLWJpZGktZm9udC13ZWlnaHQ6IG5vcm1hbCI+PHNwYW4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6IOWui+S9kzsgbXNvLWFzY2lpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW47IG1zby1oYW5zaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuIj7mn6Xor6LlhoXlrrnvvJo8L3NwYW4+PC9zdHJvbmc+PHNwYW4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6IOWui+S9kzsgbXNvLWFzY2lpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW47IG1zby1oYW5zaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuIj7njrDlvIDmlL7lkITpobnplLvngrzlh7rli6TmrKHmlbDjgIHkvZPogrLmiJDnu6njgIHkvZPotKjmtYvor5XmiJDnu6nkuI7nrYnnuqfvvJs8L3NwYW4+PHNwYW4gbGFuZz0iRU4tVVMiIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQiPjxvOnA+PC9vOnA+PC9zcGFuPjwvcD4NCjxwIGNsYXNzPSJNc29Ob3JtYWwiIHN0eWxlPSJNQVJHSU4tTEVGVDogMTcuODVwdDsgVEVYVC1JTkRFTlQ6IC0xNy44NXB0OyBtc28tbGlzdDogbDAgbGV2ZWwxIGxmbzE7IHRhYi1zdG9wczogbGlzdCAxOC4wcHQiPjxzcGFuIGxhbmc9IkVOLVVTIiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBtc28tZmFyZWFzdC1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuIj48c3BhbiBzdHlsZT0ibXNvLWxpc3Q6IElnbm9yZSI+NC48c3BhbiBzdHlsZT0iRk9OVDogN3B0IFRpbWVzIE5ldyBSb21hbiI+Jm5ic3A7Jm5ic3A7Jm5ic3A7Jm5ic3A7IDwvc3Bhbj48L3NwYW4+PC9zcGFuPjxzdHJvbmcgc3R5bGU9Im1zby1iaWRpLWZvbnQtd2VpZ2h0OiBub3JtYWwiPjxzcGFuIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiDlrovkvZM7IG1zby1hc2NpaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuOyBtc28taGFuc2ktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbiI+5pWw5o2u5pu05paw77yaPC9zcGFuPjwvc3Ryb25nPjxzcGFuIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiDlrovkvZM7IG1zby1hc2NpaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuOyBtc28taGFuc2ktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbiI+5ZCE6aG56ZS754K85Ye65Yuk44CB5L2T6LSo5rWL6K+V5oiQ57up5q+P5ZGo5LiA5LiK5Y2I5pu05paw77yM5L2T6IKy6K++5oiQ57up5Zyo6ICD6K+V57uT5p2f5ZCO5LiA5ZGo5Y2z5Y+v5p+l6K+i77ybPC9zcGFuPjxzcGFuIGxhbmc9IkVOLVVTIiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0Ij48bzpwPjwvbzpwPjwvc3Bhbj48L3A+DQo8cCBjbGFzcz0iTXNvTm9ybWFsIiBzdHlsZT0iTUFSR0lOLUxFRlQ6IDE3Ljg1cHQ7IFRFWFQtSU5ERU5UOiAtMTcuODVwdDsgbXNvLWxpc3Q6IGwwIGxldmVsMSBsZm8xOyB0YWItc3RvcHM6IGxpc3QgMTguMHB0Ij48c3BhbiBsYW5nPSJFTi1VUyIgc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgbXNvLWZhcmVhc3QtZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbiI+PHNwYW4gc3R5bGU9Im1zby1saXN0OiBJZ25vcmUiPjUuPHNwYW4gc3R5bGU9IkZPTlQ6IDdwdCBUaW1lcyBOZXcgUm9tYW4iPiZuYnNwOyZuYnNwOyZuYnNwOyZuYnNwOyA8L3NwYW4+PC9zcGFuPjwvc3Bhbj48c3Ryb25nIHN0eWxlPSJtc28tYmlkaS1mb250LXdlaWdodDogbm9ybWFsIj48c3BhbiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTog5a6L5L2TOyBtc28tYXNjaWktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbjsgbXNvLWhhbnNpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW4iPuafpeivouaXtumZkDwvc3Bhbj48L3N0cm9uZz48c3BhbiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTog5a6L5L2TOyBtc28tYXNjaWktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbjsgbXNvLWhhbnNpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW4iPu+8muWQhOmhuea1i+ivlee7k+adn+WQjuS4gOWRqOiHs+aWsOWtpuacn+W8gOWtpuWQjuS4gOWRqO+8mzwvc3Bhbj48c3BhbiBsYW5nPSJFTi1VUyIgc3R5bGU9IkZPTlQtU0laRTogMTRwdCI+PG86cD48L286cD48L3NwYW4+PC9wPg0KPHAgY2xhc3M9Ik1zb05vcm1hbCIgc3R5bGU9Ik1BUkdJTi1MRUZUOiAxNy44NXB0OyBURVhULUlOREVOVDogLTE3Ljg1cHQ7IG1zby1saXN0OiBsMCBsZXZlbDEgbGZvMTsgdGFiLXN0b3BzOiBsaXN0IDE4LjBwdCI+PHNwYW4gbGFuZz0iRU4tVVMiIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IG1zby1mYXJlYXN0LWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW4iPjxzcGFuIHN0eWxlPSJtc28tbGlzdDogSWdub3JlIj42LjxzcGFuIHN0eWxlPSJGT05UOiA3cHQgVGltZXMgTmV3IFJvbWFuIj4mbmJzcDsmbmJzcDsmbmJzcDsmbmJzcDsgPC9zcGFuPjwvc3Bhbj48L3NwYW4+PHN0cm9uZyBzdHlsZT0ibXNvLWJpZGktZm9udC13ZWlnaHQ6IG5vcm1hbCI+PHNwYW4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6IOWui+S9kzsgbXNvLWFzY2lpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW47IG1zby1oYW5zaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuIj7nrqHnkIbmnI3liqHvvJo8L3NwYW4+PC9zdHJvbmc+PHNwYW4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6IOWui+S9kzsgbXNvLWFzY2lpLWZvbnQtZmFtaWx5OiBUaW1lcyBOZXcgUm9tYW47IG1zby1oYW5zaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuIj7lrabnlJ/lr7nlkITnsbvmn6Xor6Lnu5PmnpzmnInlvILorq7ogIXvvIzpppblhYjor7fogZTns7vlkIToh6rkvZPogrLor77ku7vor77mlZnluIjov5vooYzmoLjlrp7vvIzlpoLnoa7lm6Dnu5/orqHplJnor6/vvIzliJnnlLHlrabnlJ/lhpnlh7rmiJDnu6nmm7TmlLnnlLPor7fkuqTku7vor77mlZnluIjvvIzmiqXkvZPogrLpg6jmlZnlrabnrqHnkIbnu4TlrqHmoLjvvIzlubbnu4/kvZPogrLpg6jmlZnlrabkuLvku7vnrb7lrZfmibnlh4blkI7vvIznlLHmlZnlrabnrqHnkIbnu4TotJ/otKPmm7TmlLnvvJs8L3NwYW4+PHNwYW4gbGFuZz0iRU4tVVMiIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQiPjxvOnA+PC9vOnA+PC9zcGFuPjwvcD4NCjxwIGNsYXNzPSJNc29Ob3JtYWwiIHN0eWxlPSJNQVJHSU4tTEVGVDogMTcuODVwdDsgVEVYVC1JTkRFTlQ6IC0xNy44NXB0OyBtc28tbGlzdDogbDAgbGV2ZWwxIGxmbzE7IHRhYi1zdG9wczogbGlzdCAxOC4wcHQiPjxzcGFuIGxhbmc9IkVOLVVTIiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBtc28tZmFyZWFzdC1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuIj48c3BhbiBzdHlsZT0ibXNvLWxpc3Q6IElnbm9yZSI+Ny48c3BhbiBzdHlsZT0iRk9OVDogN3B0IFRpbWVzIE5ldyBSb21hbiI+Jm5ic3A7Jm5ic3A7Jm5ic3A7Jm5ic3A7IDwvc3Bhbj48L3NwYW4+PC9zcGFuPjxzdHJvbmcgc3R5bGU9Im1zby1iaWRpLWZvbnQtd2VpZ2h0OiBub3JtYWwiPjxzcGFuIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiDlrovkvZM7IG1zby1hc2NpaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuOyBtc28taGFuc2ktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbiI+54m55Yir6K+05piO77yaPC9zcGFuPjwvc3Ryb25nPjxzcGFuIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiDlrovkvZM7IG1zby1hc2NpaS1mb250LWZhbWlseTogVGltZXMgTmV3IFJvbWFuOyBtc28taGFuc2ktZm9udC1mYW1pbHk6IFRpbWVzIE5ldyBSb21hbiI+5a2m5qCh5L2T6IKy57u85ZCI5p+l6K+i57O757uf5Li65pys5a2m5pyf5Yia5byA5aeL5L2/55So77yM5Y+v6IO95a2Y5Zyo5LiN5piv5Y2B5YiG5a6M5ZaE5LmL5aSE77yM5pWs6K+35ZCE5L2N5L2/55So6ICF6LCF6Kej77yb5aaC5pyJ5aW955qE5bu66K6u5Lmf6K+35LiO5oiR5Lus6IGU57O777yM5L2/5oiR5Lus55qE5p+l6K+i57O757uf6IO95aSf5LiN5pat5a6M5ZaE77yM5pu05aW955qE5Li65bm/5aSn5biI55Sf5pyN5Yqh77yBPC9zcGFuPjxzcGFuIGxhbmc9IkVOLVVTIiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0Ij48bzpwPjwvbzpwPjwvc3Bhbj48L3A+ZGQCBA8PFgIfAQUSMjAwOS82LzEwIDEwOjQxOjA1ZGQCBQ8PFgIfAQUSMjAyMS8zLzEwIDEwOjQxOjA1ZGRkPBrm1eLEg5iJ3U7RIWEbFEN4akU=",
            "__VIEWSTATEGENERATOR": "5B21F7B0",
            "__EVENTVALIDATION": "/wEWBgLcx+b9DAKBwaG/AQLMrvvQDQLd8tGoBALWwdnoCAKM54rGBnbtXkL1yAn8wwUcXJkl3XVJVgyt",
            "dlljs": "st",
            "Button1": "登录系统"
        }
        page = self.session.post(self.index_url, data)
        return self.username in page.text

    def morning_run(self):
        page = self.session.get("https://tygl.sspu.edu.cn/SportScore/stScore.aspx?item=1")
        soup = BeautifulSoup(page.text, "html.parser")
        tables = soup.find_all("table")
        table = tables[7]
        spans = table.find_all("span")

        summary = spans[1]
        all_runs = spans[-1]

        inner_tds = summary.find_all("td")

        data1 = inner_tds[1].text  # 早操
        data2 = inner_tds[3].text  # 课外活动
        data3 = inner_tds[5].text  # 次数调整
        data4 = inner_tds[7].text  # 体育长廊

        detail_dic_list = []
        each_run = all_runs.find_all("td")
        for td_num in range(int(len(each_run) / 6)):
            name = each_run[td_num * 6 + 1].text
            date = each_run[td_num * 6 + 2].text
            time = each_run[td_num * 6 + 3].text
            state = each_run[td_num * 6 + 4].text
            detail_dic = {
                "name": name,
                "date": date,
                "begin_end_time": time,
                "state": state
            }
            detail_dic_list.append(detail_dic)

        summary_dic = {
            "morning_run": int(data1),
            "outdoor_activity": int(data2),
            "times_adjustment": int(data3),
            "other_sport": int(data4)
        }

        final_dic = {
            "summary": summary_dic,
            "details": detail_dic_list
        }

        return final_dic

