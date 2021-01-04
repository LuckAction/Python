# -*- coding:utf-8 -*-
import os

print("大文件检测脚本，列出>=50m的文件")
floder_path = input("请输入待检测的目录路径：")

# 字节bytes转化kb\m\g
def formatSize(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        print("传入的字节格式不对")
        return "Error"

    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.2fG" % (G)
        else:
            return "%.2fM" % (M)
    else:
        return "%.2fkb" % (kb)

def checkBigFile(floder_path):
    all_str = ""
    item_list = list(filter(lambda x: not x.endswith(".uuuuuuuu"), os.listdir(floder_path)))

    for file_name in item_list:
        filePath = os.path.join(floder_path, file_name)
        if os.path.isdir(filePath):
            checkBigFile(filePath)
        elif os.path.isfile(filePath):
            size = os.path.getsize(filePath)
            if size >= 50*1024*1024:
                print(file_name +": "+formatSize(size))
        else:
            print
            "it's a special file(socket,FIFO,device file)"

checkBigFile(floder_path)