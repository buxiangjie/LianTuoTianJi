# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2019-08-23 09:28
@describe:即科齿科商户贷授信接口字段必填项校验
"""
import unittest
import json
import ddt

from common.common_func import Common
from common.get_sql_data import GetSqlData
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config

logger = Logger(logger="ckshd").getlog()


@ddt.ddt
class CreditNone(unittest.TestCase):
	file = Config().get_item('File', 'jk_ckshd_required_case_file')
	excel_data = excel_table_byname(file, 'credit_none')

	@classmethod
	def setUpClass(cls):
		cls.env = 'test'
		cls.url = CreditNone.excel_data[0]['url']
		cls.headers = CreditNone.excel_data[0]['headers']
		cls.param = CreditNone.excel_data[0]['param']

	def tearDown(self):
		pass

	@ddt.data(*excel_data)
	def test_credit_apply(self, data):
		case = data['casename']
		print(case)
		user = Common.get_userinfo()
		param = json.loads(self.param)
		param["personalInfo"].update(
			{
				"custName": user["name"],
				"cardNum": user["id"]
			}
		)
		key = str(case).split("空")[1].split(".")[0]
		value = str(case).split("空")[1].split(".")[1]
		param[key][value] = None
		headers = json.loads(self.headers)
		rep = Common.response(
			faceaddr=self.url,
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product='cloudloan',
			environment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data['resultCode']))


@ddt.ddt
class ApplyNone(unittest.TestCase):
	file = Config().get_item('File', 'jk_ckshd_required_case_file')
	excel_data = excel_table_byname(file, 'apply_none')

	@classmethod
	def setUpClass(cls):
		cls.env = 'test'
		cls.url = ApplyNone.excel_data[0]['url']
		cls.headers = ApplyNone.excel_data[0]['headers']
		cls.param = ApplyNone.excel_data[0]['param']

	def tearDown(self):
		pass

	def credit(self):
		data = excel_table_byname(self.file, 'credit')
		Common.p2p_get_userinfo('jk_ckshd_6_periods', self.env)
		self.r.mset(
			{
				"jk_ckshd_6_periods_sourceUserId": Common.get_random('userid'),
				'jk_ckshd_6_periods_transactionId': Common.get_random('transactionId'),
				"jk_ckshd_6_periods_phone": Common.get_random('phone'),
				"jk_ckshd_6_periods_firstCreditDate": Common.get_time()
			}
		)
		param = json.loads(data[0]['param'])
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('jk_ckshd_6_periods_cardNum'),
				"custName": self.r.get('jk_ckshd_6_periods_custName'),
				"phone": self.r.get('jk_ckshd_6_periods_phone')
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time()})
		param['entityInfo']['unifiedSocialCreditCode'] = Common.get_random("businessLicenseNo")
		param.update(
			{
				"sourceUserId": self.r.get('jk_ckshd_6_periods_sourceUserId'),
				"serviceSn": Common.get_random('serviceSn'),
				"transactionId": self.r.get('jk_ckshd_6_periods_transactionId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))
		self.r.mset(
			{
				"jk_ckshd_6_periods_creditId": rep['content']['creditId'],
				"jk_ckshd_6_periods_userId": rep['content']['userId']
			}
		)

	def query_result(self):
		GetSqlData.credit_set(
			environment=self.env,
			credit_id=self.r.get("jk_ckshd_6_periods_creditId")
		)
		data = excel_table_byname(self.file, 'query_result')
		param = json.loads(data[0]['param'])
		param.update({"creditId": self.r.get('jk_ckshd_6_periods_creditId')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(int(data[0]['resultCode']), rep['resultCode'])
		self.assertEqual(rep['content']['creditStatus'], 1)

	@ddt.data(*excel_data)
	def test_apply(self, data):
		self.credit()
		self.query_result()
		case = data['casename']
		print(case)
		user = Common.get_userinfo()
		param = json.loads(self.param)
		param["personalInfo"].update(
			{
				"custName": user["name"],
				"cardNum": user["id"]
			}
		)
		key = str(case).split("空")[1].split(".")[0]
		value = str(case).split("空")[1].split(".")[1]
		param[key][value] = None
		headers = json.loads(self.headers)
		rep = Common.response(
			faceaddr=self.url,
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product='cloudloan',
			environment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data['resultCode']))


if __name__ == '__main__':
	unittest.main()
