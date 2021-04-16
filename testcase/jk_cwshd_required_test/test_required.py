# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2019-08-23 09:28
@describe:宠物商户贷接口字段必填项校验
"""
import unittest
import json
import ddt

from common.common_func import Common
from common.get_sql_data import GetSqlData
from common.open_excel import excel_table_byname
from config.configer import Config


@ddt.ddt
class CreditNone(unittest.TestCase):
	file = Config().get_item('File', 'jk_cwshd_required_case_file')
	excel_data = excel_table_byname(file, 'credit_none')

	@classmethod
	def setUpClass(cls):
		cls.env = 'test'
		cls.url = CreditNone.excel_data[0]['url']
		cls.headers = CreditNone.excel_data[0]['headers']
		cls.param = CreditNone.excel_data[0]['param']
		cls.r = Common.conn_redis(cls.env)

	def tearDown(self):
		pass

	@ddt.data(*excel_data)
	def test_credit_apply(self, data):
		"""授信申请参数校验"""
		case = str(data['casename'])
		print(case)
		red = Common.p2p_get_userinfo(environment=self.env, frame="pytest")
		param = json.loads(self.param)
		param["personalInfo"].update(
			{
				"custName": self.r.get(red["user_name"]),
				"cardNum": self.r.get(red["id_card"])
			}
		)
		print(f"""前置条件:{data["前置条件"]}""")
		if len(data["前置条件"]) > 0:
			preconditions = data["前置条件"].split(",")
			for k in preconditions:
				key = k.split(".")[0]
				value = k.split(".")[1].split("==")[0]
				enum = k.split(".")[1].split("==")[1]
				if Common.is_number(enum):
					enum = int(enum)
				param[key][value] = enum
		if "==" in case:
			_key = case.split("围")[1].split(".")[0]
			_value = case.split("围")[1].split(".")[1].split("==")[0]
			_enum = case.split("==")[1].replace(" ", "")
			if Common.is_number(_enum):
				if _enum.isdigit():
					_enum = int(_enum)
				else:
					_enum = float(_enum)
			param[_key][_value] = _enum
		elif "." in case:
			_key = case.split("空")[1].split(".")[0]
			_value = case.split("空")[1].split(".")[1]
			if _key == _value:
				param[_key] = None
			else:
				param[_key][_value] = None
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
	file = Config().get_item('File', 'jk_cwshd_required_case_file')
	excel_data = excel_table_byname(file, 'apply_none')

	@classmethod
	def setUpClass(cls):
		cls.env = 'test'
		cls.url = ApplyNone.excel_data[0]['url']
		cls.headers = ApplyNone.excel_data[0]['headers']
		cls.param = ApplyNone.excel_data[0]['param']
		cls.r = Common.conn_redis(environment=cls.env)

	def tearDown(self):
		pass

	def credit(self, red):
		print("授信------")
		data = excel_table_byname(Config().get_item('File', 'jk_cwshd_case_file'), 'credit')
		self.r.setex(red["source_user_id"], 72000, Common.get_random("userid"))
		self.r.setex(red["transaction_id"], 72000, Common.get_random('transactionId'))
		self.r.setex(red["phone"], 72000, Common.get_random('phone'))
		self.r.setex(red["first_credit_date"], 72000, Common.get_time())
		param = json.loads(data[0]['param'])
		param['personalInfo'].update(
			{
				"cardNum": self.r.get(red["id_card"]),
				"custName": self.r.get(red["user_name"]),
				"phone": self.r.get(red["phone"])
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time()})
		param['entityInfo']['unifiedSocialCreditCode'] = Common.get_random("businessLicenseNo")
		param.update(
			{
				"sourceUserId": self.r.get(red["source_user_id"]),
				"serviceSn": Common.get_random('serviceSn'),
				"transactionId": self.r.get(red["transaction_id"])
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
		self.r.setex(red["credit_id"], 72000, rep['content']['creditId'])
		self.r.setex(red["user_id"], 72000, rep['content']['userId'])

	def query_result(self, red):
		print("授信结果检查-------")
		GetSqlData.credit_set(
			environment=self.env,
			credit_id=self.r.get(red["credit_id"])
		)
		GetSqlData.check_user_amount(user_id=self.r.get(red["user_id"]), environment=self.env)
		data = excel_table_byname(Config().get_item('File', 'jk_cwshd_case_file'), 'query_result')
		param = json.loads(data[0]['param'])
		param.update({"creditId": self.r.get(red["credit_id"])})
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
		red =Common.p2p_get_userinfo(environment=self.env, frame="pytest")
		self.credit(red)
		self.query_result(red)
		case = str(data['casename'])
		print(case)
		param = json.loads(self.param)
		param.update(
			{
				"sourceProjectId": Common.get_random("sourceProjectId"),
				"sourceUserId": self.r.get(red["source_user_id"]),
				"transactionId": self.r.get(red["transaction_id"])
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": self.r.get(red["id_card"]),
				"custName": self.r.get(red["user_name"]),
				"phone": self.r.get(red["phone"])
			}
		)
		param["applyInfo"]["applyAmount"] = 30000
		param["loanInfo"]["loanAmount"] = 30000
		param["cardInfo"]["unifiedSocialCreditCode"] = Common.get_random("businessLicenseNo")
		print(f"""前置条件:{data["前置条件"]}""")
		if len(data["前置条件"]) > 0:
			preconditions = data["前置条件"].split(",")
			for k in preconditions:
				key = k.split(".")[0]
				value = k.split(".")[1].split("==")[0]
				enum = k.split(".")[1].split("==")[1]
				if Common.is_number(enum):
					enum = int(enum)
				param[key][value] = enum
		if "==" in case:
			_key = case.split("围")[1].split(".")[0]
			_value = case.split("围")[1].split(".")[1].split("==")[0]
			_enum = case.split("==")[1].replace(" ", "")
			if Common.is_number(_enum):
				if _enum.isdigit():
					_enum = int(_enum)
				else:
					_enum = float(_enum)
			param[_key][_value] = _enum
		elif "." in case:
			_key = case.split("空")[1].split(".")[0]
			_value = case.split("空")[1].split(".")[1]
			if _key == _value:
				param[_key] = None
			else:
				param[_key][_value] = None
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
