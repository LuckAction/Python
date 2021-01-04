#!/usr/bin/python
# encoding:utf-8



import os
import shutil
import base64
import json


def write_binary(filePath,content):
    File = open(filePath, 'wb')
    try:
        File.write(content)
    finally:
        File.close()
    pass

def write_file(FileName, Content, optype='w'):
    File = open(FileName, optype)
    try:
        Str = str(Content)
        File.write(Str)
    finally:
        File.close()
    pass

def read_file(FileName, optype='r'):
    if os.path.exists(FileName):
        File = open(FileName, optype)
        R = ''
        try:
            R = File.read()
        finally:
            File.close()
        return R
    else:
        return ""

def encode_file(filePath, password):
	print("---------->"+filePath)
	info = read_file(filePath, 'rb')
	print(info)

	data = bytearray(info)
	length = len(data)
	code = max(password % 100, 11)
	num = 0
	while num < length:
		data[num] = data[num] ^ code
		num = num + password
	print(length)
	write_binary(filePath, data)
	pass

def decode_file(filePath, password):
	encode_file(filePath, password)


def encode_base64_file(filePath):
	info = read_file(filePath, 'rb')
	print(info)

	baseStr = base64.b64encode(info)
	print('重新base64加密结果：\n')
	print(baseStr)

	data = bytearray(baseStr)
	write_binary(filePath, data)

def decode_base64_file(filePath,gameId,iap):
	info = read_file(filePath, 'rb')

	baseStr = base64.b64decode(info)
	dictValue = eval(baseStr)
	print('替换前：\n')
	print(dictValue)
	dictValue["gameId"] = gameId
	dictValue["iap"] = iap
	print('替换后：\n')
	print(dictValue)
	value = str(dictValue)

	data = bytearray(value.encode('utf-8'))
	write_binary(filePath, data)



if __name__ == '__main__':
	#"/Volumes/data/work/小游戏/黑洞契约/BlackHoleContract_unity/Data/Raw/syscfg.json"
	#path = "/Volumes/data/work/小游戏/黑洞契约/BlackHoleContract_unity/Data/Raw/rescfg.dat"
	# for path in paths:
	path = input("请输入文件地址：")

	gameID = input("请输入gameId：")
	productId = input("请输入productId：")
	#加密
	#encode_base64_file(path)
	#encode_file(path,10)
		#解密
	decode_file(path, 10)
	decode_base64_file(path, gameID, productId)

	encode_base64_file(path)
	encode_file(path, 10)
	path = input("执行完成")
