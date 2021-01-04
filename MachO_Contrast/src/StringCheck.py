# -*- coding:utf-8 -*-

import os
import shutil
import difflib
import codecs
import Levenshtein
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# 第三方 SMTP 服务
mail_host = "smtp.163.com"  # SMTP服务器
mail_user = "15521437974@163.com"  # 用户名
mail_pass = "ITLHSGCQVBTQLFVA"  # 密码(这里的密码不是登录邮箱密码，而是授权码)

sender = '15521437974@163.com'  # 发件人邮箱
receivers = ['chenhn766@mingchao.com']  # 接收人邮箱
needReport = input("是否需要接受报告邮件？y/n：")
if needReport is 'y':
    mail_address = input("请输入邮件地址：")
    receivers.append(mail_address)

def checkFloder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(path+"目录创建成功！")

father_floder = os.path.abspath(os.path.dirname(sys.argv[0]) + os.path.sep + ".")
#father_floder = "/Volumes/data/主工程源码字符分析"
oldSourcePath = os.path.join(father_floder, 'oldSourcePath') # 旧ipa的文件夹
checkFloder(oldSourcePath)

newPath = os.path.join(father_floder, 'new') # 带采集的包存放的文件夹
checkFloder(newPath)

historyPath = os.path.join(father_floder, 'history') #旧数据存放的文件夹
checkFloder(historyPath)

waitingPath = os.path.join(father_floder, 'waiting')  #新采集数据临时存放的文件夹
checkFloder(waitingPath)

reportPath = os.path.join(father_floder, 'report')  #报告存放的文件夹
checkFloder(reportPath)

new_floder_names = list(filter(lambda x: not x.endswith(".DS_Store"), os.listdir(newPath)))


print("当前文件路径为：", father_floder)
def recordOneItem(floder_path):
    all_str = ""
    item_list = list(filter(lambda x: not x.endswith(".DS_Store"), os.listdir(floder_path)))

    for file_name in item_list:
        filePath = os.path.join(floder_path, file_name)
        if os.path.isdir(filePath):
            all_str = all_str + " " + recordOneItem(filePath)
        elif os.path.isfile(filePath):
            if filePath.endswith(".h") or filePath.endswith(".m") or filePath.endswith(".mm") or filePath.endswith(".hpp") or filePath.endswith(".cpp")  or filePath.endswith(".swift"):
                f_file = open(filePath)
                file_str = f_file.read()
                all_str = all_str + " " + file_str
                f_file.close

        else:
            print
            "it's a special file(socket,FIFO,device file)"

    return all_str
#读取出所有源码
def recordNewFloder():

    for floder_name in new_floder_names:
        print('正在读取：' + floder_name)
        textName = floder_name
        text_path = os.path.join(waitingPath, textName + '.text')
        i = 0
        floder_Path = os.path.join(newPath, floder_name)
        all_str = recordOneItem(floder_Path)

        f_allText = open(text_path, 'w')
        f_allText.write(all_str)
        f_allText.close

        shutil.move(floder_Path, oldSourcePath)
    print('读取完成，共读取了', len(new_floder_names), '个项目文件夹')

def checkDifferences(conteOne, pathTwo):
    print("conteOne长度：", len(conteOne))

    fbTwo = open(pathTwo)
    conteTwo = fbTwo.read()
    fbTwo.close()
    print("conteTwo长度：", len(conteTwo))

    seq = difflib.SequenceMatcher(lambda x: x == "\n" or x == " ", conteOne, conteTwo)
    quick_ratio = seq.quick_ratio()
    ratio = seq.ratio()
    sim = Levenshtein.ratio(conteOne, conteTwo)
    resulet = '\n Levenshtein相似度：' + str(sim) + '\n difflib指数范围：' + str(ratio) + "~" + str(quick_ratio)
    print(resulet)
    ratio = ((ratio + quick_ratio)/2 + sim)/2

    return (ratio, resulet)

def checkOldFile(x, newName):
    return x.endswith(".text") and not x == newName

def 进行匹配():
    textNames = list(filter(lambda x: x.endswith(".text"), os.listdir(waitingPath)))
    print('开始进行匹对...')
    for textName in textNames:
        print('------------------', textName, '----------------', '\n')
        oldNames = list(filter(lambda x: checkOldFile(x, textName), os.listdir(historyPath)))
        report = ''
        maxRatio = 0.0
        minRatio = 1.0
        allRatio = 0.0

        filePath = os.path.join(waitingPath, textName)
        fbOne = open(filePath)
        fileConte = fbOne.read()
        fbOne.close()
        proDesc = "备注：无"

        if len(fileConte) <= 50000:
            print("该包体字节量为:", len(fileConte), ",不满足5w要求")
            isGo = input("是否继续?(y/n)：")
            if isGo is 'n':
                continue
            else:
                decStr = input("请进行备注说明：")
                proDesc = "备注：" + decStr


        delFilePath = os.path.join(historyPath, textName)
        print('需要跟', len(oldNames), "组数据做对比")
        times = 0
        for oldFile in oldNames:
            oldFilePath = os.path.join(historyPath, oldFile)
            print('正在对比' + oldFile)
            # 匹配相似率
            resultItem = checkDifferences(fileConte, oldFilePath)
            result = resultItem[1]
            ratio = resultItem[0]
            # ratio = difflib.SequenceMatcher(lambda x: x in " ", filePath, oldFilePath).ratio()
            print('相似率指数:', ratio, "\n")

            maxRatio = max(maxRatio, ratio)
            minRatio = min(minRatio, ratio)
            allRatio = allRatio + ratio
            report = report + "\n" + oldFile + str(result) + "\n相似率:" + str(ratio) + "\n\n"
            times += 1

        times = max(1, times)
        shutil.copy(filePath, delFilePath)
        os.remove(filePath)
        result = "字节量为：" + str(len(fileConte) ) + "\n"
        result = result + textName + "\n\n检测完成，最大相似度为：" + str(maxRatio) + "\n最小相似度为：" + str(minRatio) + "\n平均似度为：" + str(
            allRatio / times)
        print(result)
        report = report + result
        report = report + "\n" + proDesc
        # 写入报告
        reportTextPath = os.path.join(reportPath, textName)
        with codecs.open(reportTextPath, mode='w', encoding='utf-8') as file_txt:
            file_txt.write(report)
        sendEmail(reportTextPath, textName + str(type) + "进制检测报告", result, ['chenhn766@mingchao.com'])

def sendEmail(reportPath, title, content, toPeoples):

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

recordNewFloder()
进行匹配()
