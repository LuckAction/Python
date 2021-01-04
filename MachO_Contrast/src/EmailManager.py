# -*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# 第三方 SMTP 服务
mail_host = "smtp.163.com"  # SMTP服务器
mail_user = "15521437974@163.com"  # 用户名
mail_pass = "ITLHSGCQVBTQLFVA"  # 密码(这里的密码不是登录邮箱密码，而是授权码)

sender = '15521437974@163.com'  # 发件人邮箱
receivers = ['chenhn766@mingchao.com']  # 接收人邮箱
#, 'caizy710@mingchao.com'

class EmailManager(object):
    def sendEmail(this, reportPath, title, content, toPeoples):

        message = MIMEMultipart()
        # message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
        message['From'] = "{}".format(sender)
        message['To'] = ",".join(toPeoples)
        # print(reportPath)
        part_attach = MIMEApplication(open(reportPath, 'rb').read())  # 打开附件
        part_attach.add_header('Content-Disposition', 'attachment', filename=title)  # 为附件命名
        message.attach(part_attach)  # 添加附件

        msgtext = MIMEText(content, _subtype='plain', _charset='utf-8')  ##_subtype有plain,html等格式，避免使用错误
        message.attach(msgtext)
        message['Subject'] = "App差异性报告"

        try:
            print("mail has been send ")
            print("正在发生邮件...")

            # smtpObj = smtplib.SMTP()
            # smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
            smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
            smtpObj.ehlo('smtp.163.com')
            smtpObj.login(mail_user, mail_pass)  # 登录验证
            smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print(e)

    def sendHostErrorEmail(host):

        message = MIMEMultipart()
        # message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
        message['From'] = "{}".format(sender)
        message['To'] = ",".join(receivers)
        # print(reportPath)

        content = '域名警告：' + host

        msgtext = MIMEText(content, _subtype='plain', _charset='utf-8')  ##_subtype有plain,html等格式，避免使用错误
        message.attach(msgtext)
        message['Subject'] = content

        try:
            print("mail has been send ")
            print("正在发生邮件...")
            smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
            smtpObj.ehlo('smtp.163.com')
            smtpObj.login(mail_user, mail_pass)  # 登录验证
            smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print(e)



# sendEmail('/Volumes/data/work/AppiumServer/history/2020_6_3_11_21/report.text','chenhenian')

# 发送邮件

