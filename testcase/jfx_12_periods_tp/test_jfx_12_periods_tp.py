# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date: 2019-08-20
@describe:金服侠-牙医贷一期12期产品流程用例
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

logger = Logger(logger="test_jfx_12_periods_tp").getlog()


class Jfx12PeriodTp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.cm = Common()
		cls.env = 'qa'
		cls.sql = GetSqlData()
		cls.r = cls.cm.conn_redis(enviroment=cls.env)
		file = Config().get_item('File', 'jfx_mul_case_file')
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_credit_apply(self):
		"""额度授信"""
		data = excel_table_byname(self.excel, 'credit_apply_data')
		print("接口名称:%s" % data[0]['casename'])
		self.cm.p2p_get_userinfo('jfx_12_periods', self.env)
		self.r.mset(
			{
				"jfx_12_periods_sourceUserId": self.cm.get_random('userid'),
				'jfx_12_periods_transactionId': self.cm.get_random('transactionId'),
				"jfx_12_periods_phone": self.cm.get_random('phone'),
				"jfx_12_periods_firstCreditDate": self.cm.get_time()
			}
		)
		param = json.loads(data[0]['param'])
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('jfx_12_periods_cardNum'),
				"custName": self.r.get('jfx_12_periods_custName'),
				"phone": self.r.get('jfx_12_periods_phone')
			}
		)
		param['applyInfo'].update({"applyTime": self.cm.get_time()})
		param.update(
			{
				"sourceUserId": self.r.get('jfx_12_periods_sourceUserId'),
				"serviceSn": self.cm.get_random('serviceSn'),
				"transactionId": self.r.get('jfx_12_periods_transactionId')
			}
		)

		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
			faceaddr=data[0]['url'],
			headers=headers,
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
				"jfx_12_periods_creditId": creditId,
				"jfx_12_periods_userId": userId
			}
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_101_query_result(self):
		"""授信结果查询"""
		self.sql.credit_set(
			enviroment=self.env,
			credit_id=self.r.get("jfx_12_periods_creditId")
		)
		data = excel_table_byname(self.excel, 'credit_query_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"creditId": self.r.get('jfx_12_periods_creditId')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
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

	def test_102_query_user_amount(self):
		"""用户额度查询"""
		data = excel_table_byname(self.excel, 'query_user_amount')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get('jfx_12_periods_sourceUserId'),
				"userId": self.r.get('jfx_12_periods_userId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
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

	def test_103_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = self.cm.get_json_data('data', 'jfx_credit_contract_sign.json')
		param.update(
			{
				"serviceSn": self.cm.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfx_12_periods_sourceUserId'),
				"contractType": 1,
				"sourceContractId": self.cm.get_random('userid'),
				"transactionId": self.r.get('jfx_12_periods_transactionId'),
				"associationId": self.r.get('jfx_12_periods_creditId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
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

	def test_104_project_apply(self):
		"""进件"""
		data = excel_table_byname(self.excel, 'test_project')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		self.r.set('jfx_12_periods_sourceProjectId', self.cm.get_random('sourceProjectId'))
		param.update(
			{
				"sourceProjectId": self.r.get('jfx_12_periods_sourceProjectId'),
				"sourceUserId": self.r.get('jfx_12_periods_sourceUserId'),
				"transactionId": self.r.get('jfx_12_periods_transactionId')
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('jfx_12_periods_cardNum'),
				"custName": self.r.get('jfx_12_periods_custName'),
				"phone": self.r.get('jfx_12_periods_phone')
			}
		)
		param['applyInfo'].update({"applyTime": self.cm.get_time()})
		param['cardInfo'].update(
			{
				"bankNameSub": "招商银行",
				"bankCode": "86",
				"bankCardNo": "6214830173648711",
				"unifiedSocialCreditCode": self.cm.get_random("businessLicenseNo")
			}
		)
		self.r.set("jfx_12_periods_corporateAccountName", param['cardInfo']['corporateAccountName'])
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		projectId = json.loads(rep.text)['content']['projectId']
		self.r.set('jfx_12_periods_projectId', projectId)
		self.assertEqual(int(data[0]['resultCode']), json.loads(rep.text)['resultCode'])

	def test_105_query_apply_result(self):
		"""进件结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('jfx_12_periods_projectId'),
			enviroment=self.env
		)
		data = excel_table_byname(self.excel, 'project_query_apply_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('jfx_12_periods_sourceProjectId'),
				"projectId": self.r.get('jfx_12_periods_projectId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
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

	def test_106_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = self.cm.get_json_data('data', 'jfx_credit_contract_sign.json')
		param.update(
			{
				"serviceSn": self.cm.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfx_12_periods_sourceUserId'),
				"contractType": 5,
				"sourceContractId": self.cm.get_random('userid'),
				"transactionId": self.r.get('jfx_12_periods_transactionId'),
				"associationId": self.r.get('jfx_12_periods_projectId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
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

	def test_107_contract_sign(self):
		"""上传借款合同"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = self.cm.get_json_data('data', 'jfx_borrow_periods_contract_sign.json')
		param.update(
			{
				"serviceSn": self.cm.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfx_12_periods_sourceUserId'),
				"contractType": 2,
				"sourceContractId": self.cm.get_random('userid'),
				"transactionId": self.r.get('jfx_12_periods_transactionId'),
				"associationId": self.r.get('jfx_12_periods_projectId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
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

	def test_108_pfa(self):
		"""放款"""
		data = excel_table_byname(self.excel, 'project_loan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('jfx_12_periods_sourceProjectId'),
				"projectId": self.r.get('jfx_12_periods_projectId'),
				"sourceUserId": self.r.get('jfx_12_periods_sourceUserId'),
				"serviceSn": self.cm.get_random('serviceSn'),
				"accountName": self.r.get("jfx_6_periods_corporateAccountName"),
				"bankCode": 86,
				"accountNo": "6214830173648711"  # 6227002432220410613
			}
		)
		self.r.set("jfx_12_periods_pfa_serviceSn", param['serviceSn'])
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
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
		self.sql.change_pay_status(
			enviroment=self.env,
			project_id=self.r.get('jfx_12_periods_projectId')
		)

	def test_109_pfa_query(self):
		"""放款结果查询"""
		self.sql.loan_set(
			enviroment=self.env,
			project_id=self.r.get('jfx_12_periods_projectId')
		)
		data = excel_table_byname(self.excel, 'pfa_query')
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": self.r.get('jfx_12_periods_pfa_serviceSn')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			enviroment=self.env,
			product="cloudloan"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_110_query_repaymentplan(self):
		"""还款计划查询"""
		data = excel_table_byname(self.excel, 'repayment_plan')
		param = json.loads(data[0]['param'])
		param.update({"projectId": self.r.get('jfx_12_periods_projectId')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
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
		self.r.set("jfx_12_periods_repayment_plan", json.dumps(json.loads(rep.text)['content']['repaymentPlanList']))

	# @unittest.skipUnless(sys.argv[4] == "repayment", "条件成立时执行")
	@unittest.skip("1")
	def test_112_repayment(self):
		"""还款流水推送"""
		data = excel_table_byname(self.excel, 'repayment')
		param = json.loads(data[0]['param'])
		repayment_plan_list = self.r.get("jfx_12_periods_repayment_plan")
		success_amount = 0.00
		repayment_detail_list = []
		period = 1
		for i in json.loads(repayment_plan_list):
			if i['period'] == 1:
				plan_detail = {
					"sourceRepaymentDetailId": Common.get_random("transactionId"),
					"payAmount": i['restAmount'],
					"planCategory": i['repaymentPlanType']
				}
				success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
				repayment_detail_list.append(plan_detail)
		param.update(
			{
				"sourceRequestId": Common.get_random("requestNum"),
				"projectId": self.r.get("jfx_12_periods_projectId"),
				"sourceProjectId": self.r.get("jfx_12_periods_sourceProjectId"),
				"sourceUserId": self.r.get("jfx_12_periods_sourceUserId"),
				"serviceSn": Common.get_random("serviceSn"),
				"payTime": Common.get_time("-"),
				"successAmount": success_amount,
				"period": period
			}
		)
		param['repaymentDetailList'] = repayment_detail_list
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			enviroment=self.env,
			product="cloudloan"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("1")
	# @unittest.skipUnless(sys.argv[4] == "early_repayment", "满足条件执行")
	def test_113_repayment(self):
		"""还款流水推送:提前全部结清"""
		data = excel_table_byname(self.excel, 'repayment')
		param = json.loads(data[0]['param'])
		for per in range(1, 13):
			success_amount = GetSqlData.get_repayment_amount(
				project_id=self.r.get("jfx_12_periods_projectId"), enviroment=self.env,
				period=per)
			param.update(
				{
					"projectId": self.r.get('jfx_12_periods_projectId'),
					"transactionId": self.r.get('jfx_12_periods_transactionId'),
					"sourceProjectId": self.r.get('jfx_12_periods_sourceProjectId'),
					"sourcePlanId": self.cm.get_random('sourceProjectId'),
					"sourceRepaymentId": self.cm.get_random("transactionId"),
					"planPayDate": Common.get_repaydate(12)[per - 1],
					"payTime": self.cm.get_time('-'),
					"successAmount": float(success_amount),
					"period": per
				}
			)
			for i in param['repaymentDetailList']:
				pay_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get('jfx_12_periods_projectId'),
					enviroment=self.env, period=per,
					repayment_plan_type=i['planCategory'])
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": self.cm.get_random("serviceSn"),
						"payAmount": float(pay_detail.get("cur_amount"))
					}
				)
			if len(data[0]['headers']) == 0:
				headers = None
			else:
				headers = json.loads(data[0]['headers'])
			rep = self.cm.response(
				faceaddr=data[0]['url'],
				headers=headers,
				data=json.dumps(param, ensure_ascii=False),
				enviroment=self.env,
				product="cloudloan"
			)
			print("响应信息:%s" % rep)
			print("返回json:%s" % rep.text)
			logger.info("返回信息:%s" % rep.text)
			self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "repayment", "条件成立时执行")
	@unittest.skip("1")
	def test_114_capital_flow(self):
		"""资金流水推送"""
		data = excel_table_byname(self.excel, 'cash_push')
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			project_id=self.r.get("jfx_12_periods_projectId"), enviroment=self.env, period=1)
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"projectId": self.r.get("jfx_12_periods_projectId"),
				"sourceProjectId": self.r.get("jfx_12_periods_sourceProjectId"),
				"repaymentPlanId": Common.get_random("sourceProjectId"),
				"sucessAmount": float(success_amount),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"tradeTime": Common.get_time(),
				"finishTime": Common.get_time()
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = self.cm.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			enviroment=self.env,
			product="cloudloan"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))


if __name__ == '__main__':
	unittest.main()
