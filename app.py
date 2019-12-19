from flask import Flask
from flask import request
from src.eams_crawler.login import Login
import json
from src.eams_crawler.lib.sessionManager import Session
from src.eams_crawler.exception import exceptions
from src.eams_crawler.lib import EAMS, OA
from src.eams_crawler.database import dao, connect
import traceback
from src.eams_crawler.stu_card import StuCard
from src.eams_crawler.stu_score import SportScore
import base64
from src.service.mail import Mail

app = Flask(__name__)

ip = "139.224.8.240"


@app.route("/check_user", methods=['GET'])
def check_user():
    username = str(request.values.get("username"))
    password = base64.b64decode(str(request.values.get("password")))

    login = Login(username, password)


@app.route('/signup', methods=['POST'])
def signup():
    if request.remote_addr == ip or request.remote_addr == "127.0.0.1":
        try:
            username = str(request.values.get("username"))
            password = str(request.values.get("password"))

            print("username: "+username + " ,password: "+password)

            if (username and password) is not None:
                log = Login(username, password)
                state = log.log()

                if state == 0 or state == 1:
                    rs, session = Session(username, password, log.db).add()

                    if rs:
                        dic = {
                            'state': state,
                            'session': session
                        }
                        log.db.commit()

                    else:
                        raise exceptions.DatabaseException("de5")
            else:
                raise exceptions.CrawlerException("ce2")  # 输入为空

        except exceptions.DatabaseException as e:  # 数据库存储错误
            log.db.rollback()
            log.db.commit()
            dic = {'state': e.reason}

            error_mes = traceback.format_exc()
            mail = Mail()
            mail.send("爬虫数据库错误", "学号: " + username + "\n密码: " + password + "\n\n" + dic + "\n" + error_mes)

        except exceptions.CrawlerException as e:
            dic = {"state": e.reason}

            error_mes = traceback.format_exc()
            mail = Mail()
            mail.send("爬虫app.py错误", "学号: " + username + "\n密码: " + password + "\n\n" + dic + "\n" + error_mes)

        except Exception:
            traceback.print_exc()
            log.db.rollback()
            log.db.commit()
            dic = {'state': -1}   # 未知错误

            error_mes = traceback.format_exc()
            mail = Mail()
            mail.send("爬虫未知错误", "学号: " + username + "\n密码: " + password + "\n\n" + error_mes)

        finally:
            return json.dumps(dic)


@app.route('/')
def index():
    return "forbidden api"


@app.route('/user/course/update', methods=['GET'])   # 0:无参数，1：成功，"ce3"/"ce4"：密码对错误，"-1"：未知错误，"ce5": 用户没有课表, "ce7":未评教
def course_update(username,password,system,stuid,semester):
    # if request.remote_addr == ip or request.remote_addr == "127.0.0.1":
    #     username = str(request.values.get("username"))
    #     system = str(request.values.get("system"))   # 0: OA, 1: EAMS
    #     password = base64.b64decode(str(request.values.get("password")))
    #     stuid = str(request.values.get("stuid"))
    #     semester = str(request.values.get("semester"))
    #
        # database_obj = connect.Database()
    #
        dic = {"state": 1}

        try:
            if system == "0":
                oa_session = OA.OASession(username=username, password=password)
                if oa_session.login():
                    eams_parser = EAMS.EAMSParser(oa_session)
                    dic_list = eams_parser.get_course_table_with_stuid(stuid, semester)
                    if dic_list is not None:
                        # rs = dao.UsernameCourseIdDao(database_obj).update(dic_list, username, semester)
                        # database_obj.commit()
                        # dic = {"state": 1}
                        return dic_list
                    else:
                        raise exceptions.CrawlerException("ce5")
                else:
                    raise exceptions.CrawlerException("ce3")

            elif system == "1":
                eams_session = EAMS.EAMSSession(username=username, password=password)
                if eams_session.login():
                    eams_parser = EAMS.EAMSParser(eams_session)
                    dic_list = eams_parser.get_course_table_with_stuid(stuid, semester)
                    if dic_list is not None:
                        # rs = dao.UsernameCourseIdDao(database_obj).update(dic_list, username, semester)
                        # database_obj.commit()
                        # # dic = {"state": 1}
                        return dic_list
                    else:
                        raise exceptions.CrawlerException("ce5")
                else:
                    raise exceptions.CrawlerException("ce4")

        except exceptions.CrawlerException as e:
            dic = {"state": e.reason}
            return json.dumps(dic)

        except Exception:
            traceback.print_exc()
            dic = {"state": -1}
            return json.dumps(dic)
            # database_obj.rollback()
            # database_obj.commit()
        #
        # finally:
        #     return json.dumps(dic)


@app.route('/user/card/transaction', methods=['GET'])
def card_transaction(username,password,begin_date,end_date):     # -1：未知错误，ce6:无交易数据，ce3：OA密码错误；返回交易list
    try:
        # username = str(request.values.get("username"))
        # password = base64.b64decode(str(request.values.get("password")))
        # begin_date = str(request.values.get("begin_date"))
        # end_date = str(request.values.get("end_date"))

        stu_card = StuCard(username, password, begin_date, end_date)
        transactions = stu_card.transaction()
        return json.dumps(transactions, ensure_ascii=False)

    except exceptions.CrawlerException as e:
        dic = {"state": e.reason}
        return json.dumps(dic)

    except Exception:
        traceback.print_exc()
        dic = {"state": -1}
        return json.dumps(dic)


@app.route('/user/score/sport/run', methods=['GET'])
def sport_morning_run(username,password):     # -1：未知错误，ce8:爬虫获取失败，ce3：OA密码错误；成功返回晨跑总数据和每次晨跑数据
    try:
        # username = str(request.values.get("username"))
        # password = base64.b64decode(str(request.values.get("password")))

        sport = SportScore(username, password)
        return json.dumps(sport.morning_run())

    except exceptions.CrawlerException as e:
        dic = {"state": e.reason}
        return json.dumps(dic)

    except Exception:
        traceback.print_exc()
        dic = {"state": -1}
        return json.dumps(dic)


if __name__ == '__main__':
    app.run(threaded=True)
