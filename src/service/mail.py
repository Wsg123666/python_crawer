import smtplib
from email.mime.text import MIMEText
from email.header import Header


class Mail:
    mail_host = "smtp.exmail.qq.com"  # 设置服务器
    port = 465
    mail_user = "wsg@zhishu.app"  # 用户名
    mail_pass = "Wushiguang440295."  # 口令
    admin_email = ["20181130340@stu.sspu.edu.cn"]

    def send(self, title, content):
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = Header("知书服务器", 'utf-8')
        message['To'] = Header("管理员", 'utf-8')

        message['Subject'] = Header(title, 'utf-8')

        try:
            smtpObj = smtplib.SMTP_SSL()
            smtpObj.connect(self.mail_host, self.port)
            smtpObj.login(self.mail_user, self.mail_pass)
            smtpObj.sendmail(self.mail_user, self.admin_email, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")

