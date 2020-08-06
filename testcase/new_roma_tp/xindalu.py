#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:
"""
import sys
import time
import json
import requests
import xlwt
import os
from common.open_excel import excel_table_byname
from config.configer import Config

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


def dl():
	global re, cws
	excel = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + Config().Get_Item('File', 'xindalu')
	data = excel_table_byname(excel, by_name='Sheet2')
	name = []
	idcard = []
	result = []
	score = []
	quota = []
	rule_list = []
	hit_category = []
	pa = []
	for i in range(0, len(data)):
		if data[i]['性别'] == 'M':
			sex = '1'
		else:
			sex = '0'
		# if '北京' in data[i]['经营地址（省）']:
		# 	province = '0'
		# else:
		# 	province = '1'
		# purchaseQuantity = round(int(data[i]['车置宝平台交易总笔数']) / (round((data[i]['车置宝平台注册天数']) / 365, 1)))
		# totalAmt = round(float(data[i]['车置宝平台交易总金额']) / round((data[i]['车置宝平台注册天数']) / 365, 1))
		day1 = time.strptime(str(data[i]['首次授信时间']).split(' ')[0], '%Y-%m-%d')
		now = time.strftime("%Y-%m-%d", time.localtime())
		day2 = time.strptime(now, '%Y-%m-%d')
		creditYears = str(round(((int(time.mktime(day2)) - int(time.mktime(day1))) / (
				24 * 60 * 60) / 365), 1))
		if int(data[i]['车位数']) == 0:
			cws = 3
		elif int(data[i]['车位数']) == 1:
			cws = 8
		elif int(data[i]['车位数']) == 2:
			cws = 15
		elif int(data[i]['车位数']) == 3:
			cws = 25
		elif int(data[i]['车位数']) == 4:
			cws = 35
		param = {
			"productCode": "00120181119435572",
			"requestParam": {
				"name": data[i]['姓名'],
				"id_card": data[i]['身份证号码'],
				"phone_no": str(int(data[i]['手机号码'])),
				"age": str(int(data[i]['年龄'])),
				"sex": sex,  # 性别
				"maritalStatus": str(int(data[i]['婚姻状况'])),
				"hasChildern": str(int(data[i]['是否有子女'])),
				"liveStatus": str(int(data[i]['是否购房'])),
				"manageTime": str(int(data[i]['经营年限'])),
				"employeeNum": int(data[i]['员工数目']),
				# "stallNum": cws,  # 车位数
				"stallNum": int(data[i]['车位数']),
				"disburseNum": str(int(data[i]['累计借款次数'])),
				# "province": province,  # 经营地区
				"province": int(data[i]['经营地址']),
				# "avgAmt": data[i]['车置宝平台交易平均车价'],
				# "purchaseQuantity": purchaseQuantity,  # 年车采购量
				# "totalAmt": totalAmt,  # 总额
				"creditYears": creditYears,  # 授信年数
				"totalAmt": data[i]['企业年车相关流水总额'],
				"avgAmt": data[i]['企业类提车交易平均金额'],
				"purchaseQuantity": data[i]['企业年车采购量']
				# "sellCarNum": data[i]['企业每车位年销售车数量']
			}
		}
		print(param)
		header = {
			"Content-Type": "application/json"
		}
		# params = {
		# 	"productCode": "00120181119435572",
		# 	"requestParam": {
		# 		"name": "辛恬",
		# 		"id_card": "411528199207132134",
		# 		"phone_no": "17600299420",
		# 		"sex": "1",
		# 		"maritalStatus": "1",
		# 		"hasChildern": "1",
		# 		"liveStatus": "1",
		# 		"manageTime": "2",
		# 		"employeeNum": "6",
		# 		"stallNum": int(data[i]['车位数']),
		# 		"disburseNum": str(int(data[i]['累计借款次数'])),
		# 		# "province": province,
		# 		# "avgAmt": data[i]['车置宝平台交易平均车价'],
		# 		# "totalAmt": data[i]['车置宝平台交易总金额']
		# 	}
		# }
		"""
		# 百融测试http://39.105.152.212:8082/decision/sync/get    百融正式http://39.107.115.172:8082/decision/sync/get
		# 百融正式环境#bairongCreditAndBlackUrl: https://decision.igfax.com/decision/sync/get
		"""
		try:
			re = requests.post(url="https://decision.igfax.com/decision/sync/get", headers=header,
							   data=json.dumps(param, ensure_ascii=False).encode('utf-8'))
		except Exception as e:
			print(str(e))
		rep = json.loads(re.text)
		resu = rep['decisionResult']['result']
		sc = rep['decisionResult']['score']
		if resu == '拒绝':
			qu = '0'
		else:
			qu = rep['decisionResult']['quota']
		rl = str(rep['decisionResult']['resultMap']['rule_list'])
		hc = str(rep['decisionResult']['resultMap']['hit_ category'])
		name.append(data[i]['姓名'])
		idcard.append(data[i]['身份证号码'])
		result.append(resu)
		score.append(sc)
		quota.append(qu)
		rule_list.append(rl)
		hit_category.append(hc)
		pa.append(str(param))
		print(resu, score, quota, rule_list, hit_category)
	workbook = xlwt.Workbook(encoding='utf-8')
	worksheet = workbook.add_sheet('Sheet1', cell_overwrite_ok=False)
	title = ['姓名', '身份证号', '分数', '额度', '命中欺诈规则', '命中欺诈类型', '风控结果', '请求数据']
	for n in range(0, len(title)):
		worksheet.write(0, n, title[n])
	for n in range(0, len(name)):
		worksheet.write(n + 1, 0, name[n])
	for n in range(0, len(idcard)):
		worksheet.write(n + 1, 1, idcard[n])
	for n in range(0, len(score)):
		worksheet.write(n + 1, 2, score[n])
	for n in range(len(quota)):
		worksheet.write(n + 1, 3, quota[n])
	for n in range(len(rule_list)):
		worksheet.write(n + 1, 4, rule_list[n])
	for n in range(len(hit_category)):
		worksheet.write(n + 1, 5, hit_category[n])
	for n in range(len(result)):
		worksheet.write(n + 1, 6, result[n])
	for n in range(len(pa)):
		worksheet.write(n + 1, 7, pa[n])
	workbook.save(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/data/xindalu.xls')


if __name__ == '__main__':
	dl()
