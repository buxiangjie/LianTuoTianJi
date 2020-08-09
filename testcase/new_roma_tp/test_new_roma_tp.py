#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2020.02.15 15:25
@describe:新罗马车贷业务流程接口
"""

import unittest
import os
import json
import time
import sys

from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = Logger(logger="test_new_roma_tp").getlog()


class NewRomaTp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = sys.argv[3]
		cls.r = Common.conn_redis(enviroment=cls.env)
		file = Config().get_item('File', 'new_roma_case_file')
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_credit_apply(self):
		"""额度授信"""
		data = excel_table_byname(self.excel, 'credit_apply_data_new')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('new_roma', self.env)
		self.r.mset(
			{
				"new_roma_sourceUserId": Common.get_random('userid'),
				"new_roma_transactionId": Common.get_random('transactionId'),
				"new_roma_phone": Common.get_random('phone'),
				"new_roma_firstCreditDate": Common.get_time(),
			}
		)
		param = json.loads(data[0]['param'])
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('new_roma_cardNum'),
				"custName": self.r.get('new_roma_custName'),
				"phone": self.r.get('new_roma_phone')
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time()})
		param['riskSuggestion'].update(
			{"firstCreditDate": self.r.get('new_roma_firstCreditDate')})
		param.update(
			{
				"sourceUserId": self.r.get('new_roma_sourceUserId'),
				"serviceSn": Common.get_random('serviceSn'),
				"transactionId": self.r.get('new_roma_transactionId')
			}
		)
		param['orderDetail']['employeeNum'] = 10
		param['phoneInfoList'][0].update(
			{
				"isSelf": "Y",
				"phoneStatus": 1,
				"timeLength": 24
			}
		)
		# param['applyInfo']['productCode'] = 'XJ_ROMA_CAR'
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'], headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		creditId = json.loads(rep.text)['content']['creditId']
		userId = json.loads(rep.text)['content']['userId']
		self.r.mset(
			{
				"new_roma_creditId": creditId,
				"new_roma_userId": userId
			}
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_101_upload_image(self):
		"""图片上传：授信"""
		data = excel_table_byname(self.excel, 'image_upload')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"associationId": self.r.get('new_roma_creditId'),
				"bizType": 1
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
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_1011_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'roma_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('new_roma_sourceUserId'),
				"contractType": 1,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('new_roma_transactionId'),
				"associationId": self.r.get('new_roma_creditId')
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
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_102_query_result(self):
		"""授信结果查询"""
		time.sleep(3)
		GetSqlData.credit_set(enviroment=self.env, credit_id=self.r.get("new_roma_creditId"))
		data = excel_table_byname(self.excel, 'credit_query_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"creditId": self.r.get('new_roma_creditId')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_103_query_user_amount(self):
		"""用户额度查询"""
		data = excel_table_byname(self.excel, 'query_user_amount')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get('new_roma_sourceUserId'),
				"userId": self.r.get('new_roma_userId'),
				# "productCode": "XJ_ROMA_CAR"
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
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))
		GetSqlData.check_user_amount(
			user_id=self.r.get('new_roma_userId'),
			enviroment=self.env
		)

	def test_104_project_apply(self):
		"""进件"""
		data = excel_table_byname(self.excel, 'test_project')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		self.r.set('new_roma_sourceProjectId', Common.get_random('sourceProjectId'))
		param.update(
			{
				"sourceProjectId": self.r.get('new_roma_sourceProjectId'),
				"sourceUserId": self.r.get('new_roma_sourceUserId'),
				"transactionId": self.r.get('new_roma_transactionId')
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('new_roma_cardNum'),
				"custName": self.r.get('new_roma_custName'),
				"phone": self.r.get('new_roma_phone'),
				"hasChildren": "Y"
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time(),
				# "productCode": "XJ_ROMA_CAR"
			}
		)
		param['riskSuggestion'].update(
			{"firstCreditDate": self.r.get('new_roma_firstCreditDate')})
		param['cardInfo'].update(
			{
				"bankNameSub": "建设银行",
				"bankCode": "34",
				"bankCardNo": "6227002432220410613"
			}
		)
		param['extraInfo']['vin'] = Common.get_random("businessLicenseNo")
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		self.r.set('new_roma_projectId', json.loads(rep.text)['content']['projectId'])
		self.assertEqual(int(data[0]['resultCode']), json.loads(rep.text)['resultCode'])
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('new_roma_projectId'),
			enviroment=self.env)

	def test_105_query_apply_result(self):
		"""进件结果查询"""
		data = excel_table_byname(self.excel, 'project_query_apply_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('new_roma_sourceProjectId'),
				"projectId": self.r.get('new_roma_projectId')
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
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['resultCode']), json.loads(rep.text)['resultCode'])
		self.assertEqual(json.loads(rep.text)['content']['auditStatus'], 2)

	def test_106_contract_sign(self):
		"""上传借款合同"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'roma_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('new_roma_sourceUserId'),
				"contractType": 2,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('new_roma_transactionId'),
				"associationId": self.r.get('new_roma_projectId')
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
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['resultCode']), json.loads(rep.text)['resultCode'])

	def test_107_pfa(self):
		"""放款"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'project_loan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('new_roma_sourceProjectId'),
				"projectId": self.r.get('new_roma_projectId'),
				"sourceUserId": self.r.get('new_roma_sourceUserId'),
				"serviceSn": Common.get_random('serviceSn'),
				"accountName": self.r.get('new_roma_custName'),
				"id": self.r.get('new_roma_cardNum'),
				"bankCode": "CCB",
				"accountNo": "6227002432220410613"  # 6227003814170172872
			}
		)
		self.r.set("new_roma_pfa_serviceSn", param['serviceSn'])
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['resultCode']), json.loads(rep.text)['resultCode'])
		time.sleep(8)
		# 修改支付表中的品钛返回code
		GetSqlData.change_pay_status(
			enviroment=self.env,
			project_id=self.r.get('new_roma_projectId')
		)

	def test_108_query(self):
		"""放款结果查询"""
		GetSqlData.loan_set(enviroment=self.env, project_id=self.r.get('new_roma_projectId'))
		data = excel_table_byname(self.excel, 'query')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": self.r.get("new_roma_pfa_serviceSn")
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
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['resultCode']), json.loads(rep.text)['resultCode'])

	def test_109_query_repayment_plan(self):
		"""还款计划查询"""
		data = excel_table_byname(self.excel, 'query_repayment_plan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"transactionId": Common.get_random("transactionId"),
				"projectId": self.r.get('new_roma_projectId')
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
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['resultCode']), json.loads(rep.text)['resultCode'])

	def test_110_pre_clear_calculate(self):
		"""还款计划试算"""
		data = excel_table_byname(self.excel, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("new_roma_sourceProjectId"),
				"projectId": self.r.get('new_roma_projectId')
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
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['resultCode']), json.loads(rep.text)['resultCode'])

	# @unittest.skipUnless(sys.argv[4] == "offline_partial", "-")
	@unittest.skip("跳过")
	def test_111_offline_partial(self):
		"""线下还款:部分还款"""
		data = excel_table_byname(self.excel, 'offline_partial')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceRequestId": Common.get_random("requestNum"),
				"sourceRepaymentId": Common.get_random("requestNum"),
				"projectId": self.r.get("new_roma_projectId"),
				"sourceProjectId": self.r.get("new_roma_sourceProjectId"),
				"sourceUserId": self.r.get("new_roma_sourceUserId"),
				"serviceSn": Common.get_random("serviceSn"),
				"payTime": Common.get_time("-"),
				"successAmount": 76,
				"period": 1
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
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	def test_112_push_reconciliation_result(self):
		"""对账结果推送"""
		data = excel_table_byname(self.excel, 'push_reconciliation_result')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"accountId": Common.get_random("transactionId")
			}
		)
		for i in range(len(param['resultList'])):
			param['resultList'][i]['businessDate'] = Common.get_time('day')
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['resultCode']), json.loads(rep.text)['resultCode'])


if __name__ == '__main__':
	unittest.main()
