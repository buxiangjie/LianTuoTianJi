# -*- coding: UTF-8 -*-
"""
@auth:
@date:
@describe:支付系统测试
"""
import unittest
import os
import json
import sys

from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = Logger(logger="pay_tp").getlog()


class PayTp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.cm = Common()
		cls.env = 'online'
		cls.sql = GetSqlData()
		cls.r = cls.cm.conn_redis(enviroment='qa')
		file = Config().Get_Item('File', 'pay_case_file')
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	def tearDown(self):
		pass

	def test_0_sign(self):
		"""预签约"""
		data = excel_table_byname(self.excel, 'sign')
		print("接口名称:%s" % data[0]['casename'])
		self.cm.p2p_get_userinfo('pay', self.env)
		self.r.mset({
			"pay_sourceUserId": self.cm.get_random('userid'),
			"pay_requestId": self.cm.get_random('userid'),
			"pay_sourceEnterpriseCode": self.cm.get_random("transactionId"),
			"pay_sourceProjectId": self.cm.get_random("sourceProjectId"),
			"pay_mobile": self.cm.get_random("phone")
		})
		param = json.loads(data[0]['param'])
		param.update({
			"requestId": Common.get_random("serviceSn"),
			"requestTime": Common.get_time("-"),
			"sourceUserId": self.r.get("pay_sourceUserId"),
			# "name": self.r.get("pay_custName"),
			# "cardNo": self.r.get("pay_cardNum"),
			"name": "卜祥杰",
			"cardNo": "372301199509074811",
			"bankCode": "BOC",
			# "bankNo": self.r.get("pay_bankcard"),
			"bankName": "中国银行",
			# "mobile": self.r.get("pay_mobile"),
			"mobile": "18366582857",
			"bankNo": "6216600100008405977"

			# "accountType": 1,
			# "bankCardType": 3,
			# "bankValidity": "04/20",
			# "bankSafetyCode": "331",
			# "bankCode": "CMBC",
			# "bankName": "中国民生银行",
			# "bankNo": "6216910107622851",
			# "name": "卜祥杰",
			# "cardNo": "372301199509074811",
			# "mobile": "18366582857"
			# "sourceSystemCode": "123"
			# "sourceEnterpriseCode": "8482"
		})

		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product='pay',
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		signTaskId = json.loads(rep.text)['data']['signTaskId']
		self.assertEqual(json.loads(rep.text)['code'], int(data[0]['resultCode']))
		self.r.set("pay_signTaskId", signTaskId)

	def test_1_confirmSign(self):
		"""确认签约"""
		data = excel_table_byname(self.excel, 'confirmSign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'pay_confirm_sign.json')
		param.update({
			"requestId": int(self.cm.get_random("serviceSn")),
			"sourceUserId": self.r.get("pay_sourceUserId"),
			"signTaskId": self.r.get("pay_signTaskId"),
			"requestTime": Common.get_time("-")
		})

		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(faceaddr=data[0]['url'], headers=headers,
							   data=json.dumps(param, ensure_ascii=False).encode('utf-8'), product='pay',
							   enviroment=self.env)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['code'], int(data[0]['resultCode']))


if __name__ == '__main__':
	unittest.main()
