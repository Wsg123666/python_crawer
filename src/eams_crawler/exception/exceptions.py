class CrawlerException(Exception):
    def __init__(self, reason):
        self.reason = reason
# ce1: 用户提供的用户名、密码对错误
# ce2: 用户名或密码为空
# ce3: OA系统密码错误
# ce4: EAMS密码错误
# ce5: 用户没有课表
# ce6: 用户校园卡在指定时间段无交易数据
# ce7: 没有评估导师，无法获取课表
# ce8: 晨跑数据获取失败


class DatabaseException(Exception):
    def __init__(self, reason):
        self.reason = reason
# de1: 用户名密码正确，user表存储出错
# de2: user_detail表保存错误
# de3: username_courseid表保存错误
# de4: 保存用户成绩summery错误
# de5: 保存session错误
