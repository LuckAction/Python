# -*- coding:utf-8 -*-

import os
import binascii
from functools import partial
import datetime
import difflib
import shutil
import codecs
import Levenshtein
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

type = 16# 2表示识别成2进制，16为16进制
machO_floder = "/Volumes/data/小游戏"+str(type)+"进制分析" #input("请输入待检测的根目录路径：")
#machO_floder = "/Volumes/data/主工程源码16进制分析" #input("请输入待检测的根目录路径：")
delPath = os.path.join(machO_floder, 'deleteIPA') # 旧ipa的文件夹
newPath = os.path.join(machO_floder, 'new') # 带采集的包存放的文件夹
oldPath = os.path.join(machO_floder, 'old') #旧数据存放的文件夹
waitingPath = os.path.join(machO_floder, 'waiting')  #新采集数据临时存放的文件夹
reportPath = os.path.join(machO_floder, 'report')  #报告存放的文件夹
file_names = list(filter(lambda x: not x.endswith(".DS_Store"), os.listdir(newPath)))

# 发送邮件
def sendEmail(reportPath, title, content):

    message = MIMEMultipart()
    # message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
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

#读取二进制信息
def recordIPA():
    for fileName in file_names:
        print('正在读取二进制信息：' + fileName)
        textName = fileName
        i = 0
        filePath = os.path.join(newPath, fileName)
        textPath = os.path.join(waitingPath, textName + '.text')
        oldFloderPath = os.path.join(oldPath, textName + '.text')
        f = open(filePath, 'rb')
        f2 = open(textPath, 'w')
        records = iter(partial(f.read, 1), b'')
        for r in records:
            r_int = int.from_bytes(r, byteorder='big')  # 将 byte转化为 int
            if type == 2:
                str_bin = bin(r_int).lstrip('0b')  # 将int转化为二进制字符
                f2.write(str_bin)

            else:
                v = hex(r_int)
                strlist = v.split('x')
                tag = strlist[1]
                if len(tag) == 1:
                    f2.write('0' + tag + " ")
                else:
                    f2.write(tag + " ")

        f.close
        f2.close
        shutil.move(filePath, delPath)
        shutil.copy(textPath, oldFloderPath)

        # os.remove(filePath)
    print('二进制信息读取完成，共读取了', len(file_names), '个')
recordIPA()

textNames = list(filter(lambda x: x.endswith(".text"), os.listdir(waitingPath)))
print('开始进行匹对...')
def checkOldFile(x,newName):
    return x.endswith(".text") and not x == newName

def checkDifferences(pathOne, pathTwo):
    fbOne = open(pathOne)
    conteOne = fbOne.read()
    fbOne.close()
    print("conteOne长度：", len(conteOne))

    fbTwo = open(pathTwo)
    conteTwo = fbTwo.read()
    fbTwo.close()
    print("conteTwo长度：", len(conteTwo))

    seq = difflib.SequenceMatcher(None, conteOne, conteTwo).quick_ratio()
    print('相似度：', seq)

    # ratio = seq.ratio()
    #sim = Levenshtein.ratio(conteOne, conteTwo)
    #print('\nLevenshtein相似度：', sim)
    return seq

for textName in textNames:
    print('------------------', textName, '----------------', '\n')
    oldNames = list(filter(lambda x: checkOldFile(x, textName), os.listdir(oldPath)))
    report = ''
    maxRatio = 0.0
    minRatio = 1.0
    allRatio = 0.0

    filePath = os.path.join(waitingPath, textName)
    oldFilePath = os.path.join(oldPath, textName)
    print('需要跟', len(oldNames), "组数据做对比")
    times = 0
    for oldFile in oldNames:

        oldFilePath = os.path.join(oldPath, oldFile)
        print('正在对比' + oldFile)
        #匹配相似率
        ratio = checkDifferences(filePath, oldFilePath)
        #ratio = difflib.SequenceMatcher(lambda x: x in " ", filePath, oldFilePath).ratio()
        print('相似率:', ratio, "\n")

        maxRatio = max(maxRatio, ratio)
        minRatio = min(minRatio, ratio)
        allRatio = allRatio + ratio
        report = report + oldFile + "\n相似率:" + str(ratio) + "\n\n"
        times += 1

    times = max(1, times)
    shutil.copy(filePath, oldFilePath)
    os.remove(filePath)
    result = textName+"\n\n检测完成，最大相似度为："+str(maxRatio)+"\n最小相似度为："+str(minRatio)+"\n平均似度为："+str(allRatio/times)
    print(result)
    report = report + result
    # 写入报告
    reportTextPath = os.path.join(reportPath, textName)
    with codecs.open(reportTextPath, mode='w', encoding='utf-8') as file_txt:
        file_txt.write(report)
    sendEmail(reportTextPath, textName+str(type)+"进制检测报告", result)
#    addReport(reportPath, floderName + "启动堆栈比对报告，最大相似率：" + str(maxRatio) + "，平均相似率：" + str(allRatio/times), tagertName)




