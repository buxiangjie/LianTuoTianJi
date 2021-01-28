# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date: 2019-08-20
@describe:金服侠-牙医贷一期6期产品流程用例
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

logger = Logger(logger="test_jfx_6_periods_tp").getlog()


class Jfx3PeriodTp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = "qa"
		cls.r = Common.conn_redis(environment=cls.env)
		cls.file = Config().get_item('File', 'jfx_mul_case_file')

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_credit_apply(self):
		"""额度授信"""
		data = excel_table_byname(self.file, 'credit_apply_data')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('jfx_6_periods', self.env)
		self.r.mset(
			{
				"jfx_6_periods_sourceUserId": Common.get_random('userid'),
				'jfx_6_periods_transactionId': Common.get_random('transactionId'),
				"jfx_6_periods_phone": Common.get_random('phone'),
				"jfx_6_periods_firstCreditDate": Common.get_time()
			}
		)
		param = json.loads(data[0]['param'])
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('jfx_6_periods_cardNum'),
				"custName": self.r.get('jfx_6_periods_custName'),
				"phone": self.r.get('jfx_6_periods_phone')
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time()})
		param.update(
			{
				"sourceUserId": self.r.get('jfx_6_periods_sourceUserId'),
				"serviceSn": Common.get_random('serviceSn'),
				"transactionId": self.r.get('jfx_6_periods_transactionId')
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
		self.r.mset(
			{
				"jfx_6_periods_creditId": rep['content']['creditId'],
				"jfx_6_periods_userId": rep['content']['userId']
			}
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	def test_101_query_result(self):
		"""授信结果查询"""
		GetSqlData.credit_set(
			environment=self.env,
			credit_id=self.r.get("jfx_6_periods_creditId")
		)
		data = excel_table_byname(self.file, 'credit_query_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"creditId": self.r.get('jfx_6_periods_creditId')})
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

	def test_102_query_user_amount(self):
		"""用户额度查询"""
		data = excel_table_byname(self.file, 'query_user_amount')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get('jfx_6_periods_sourceUserId'),
				"userId": self.r.get('jfx_6_periods_userId')
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
		self.assertEqual(int(data[0]['resultCode']), rep['resultCode'])

	def test_103_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'jfx_credit_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfx_6_periods_sourceUserId'),
				"contractType": 1,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('jfx_6_periods_transactionId'),
				"associationId": self.r.get('jfx_6_periods_creditId')
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
		self.assertEqual(int(data[0]['resultCode']), rep['resultCode'])

	def test_104_project_apply(self):
		"""进件"""
		data = excel_table_byname(self.file, 'test_project')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		self.r.set('jfx_6_periods_sourceProjectId', Common.get_random('sourceProjectId'))
		param.update(
			{
				"sourceProjectId": self.r.get('jfx_6_periods_sourceProjectId'),
				"sourceUserId": self.r.get('jfx_6_periods_sourceUserId'),
				"transactionId": self.r.get('jfx_6_periods_transactionId')
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('jfx_6_periods_cardNum'),
				"custName": self.r.get('jfx_6_periods_custName'),
				"phone": self.r.get('jfx_6_periods_phone')
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time(),
				"applyAmount": 84920.00,
				"applyTerm": 6
			}
		)
		param['loanInfo'].update(
			{
				"loanAmount": 84920.00,
				"assetInterestRate": 0.158156,
				"userInterestRate": 0.153156,
				"loanTerm": 6
			}
		)
		param['cardInfo'].update(
			{
				"bankNameSub": "建设银行",
				"bankCode": "34",
				"bankCardNo": "6227002432220410613",
				"unifiedSocialCreditCode": Common.get_random("businessLicenseNo")
			}
		)
		self.r.set("jfx_6_periods_corporateAccountName", param['cardInfo']['corporateAccountName'])
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
		self.r.set('jfx_6_periods_projectId', rep['content']['projectId'])

	def test_105_query_apply_result(self):
		"""进件结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('jfx_6_periods_projectId'),
			environment=self.env
		)
		data = excel_table_byname(self.file, 'project_query_apply_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('jfx_6_periods_sourceProjectId'),
				"projectId": self.r.get('jfx_6_periods_projectId')
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
		self.assertEqual(int(data[0]['resultCode']), rep['resultCode'])

	def test_106_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'jfx_credit_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfx_6_periods_sourceUserId'),
				"contractType": 5,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('jfx_6_periods_transactionId'),
				"associationId": self.r.get('jfx_6_periods_projectId')
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
		self.assertEqual(int(data[0]['resultCode']), rep['resultCode'])

	def test_107_contract_sign(self):
		"""上传借款合同"""
		data = excel_table_byname(self.file, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'jfx_borrow_periods_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfx_6_periods_sourceUserId'),
				"contractType": 2,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('jfx_6_periods_transactionId'),
				"associationId": self.r.get('jfx_6_periods_projectId')
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
		self.assertEqual(int(data[0]['resultCode']), rep['resultCode'])

	def test_108_pfa(self):
		"""放款"""
		data = excel_table_byname(self.file, 'project_loan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('jfx_6_periods_sourceProjectId'),
				"projectId": self.r.get('jfx_6_periods_projectId'),
				"sourceUserId": self.r.get('jfx_6_periods_sourceUserId'),
				"serviceSn": Common.get_random('serviceSn'),
				"accountName": self.r.get("jfx_6_periods_corporateAccountName"),
				"bankCode": "34",
				"amount": 84920.00,
				"accountNo": "6227002432220410613"  # 6227003814170172872
			}
		)
		self.r.set("jfx_6_periods_pfa_serviceSn", param['serviceSn'])
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
		time.sleep(8)
		GetSqlData.change_pay_status(
			environment=self.env,
			project_id=self.r.get('jfx_6_periods_projectId')
		)
		GetSqlData.loan_set(
			environment=self.env,
			project_id=self.r.get('jfx_6_periods_projectId')
		)

	def test_109_pfa_query(self):
		"""放款结果查询"""
		data = excel_table_byname(self.file, 'pfa_query')
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": self.r.get('jfx_6_periods_pfa_serviceSn')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			environment=self.env,
			product="cloudloan"
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	def test_110_query_repaymentplan(self):
		"""还款计划查询"""
		data = excel_table_byname(self.file, 'repayment_plan')
		param = json.loads(data[0]['param'])
		param.update({"projectId": self.r.get('jfx_6_periods_projectId')})
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
		self.r.set("jfx_6_periods_repayment_plan", json.dumps(rep['content']['repaymentPlanList']))

	# @unittest.skipUnless(sys.argv[4] == "repayment", "条件成立时执行")
	@unittest.skip("11")
	def test_112_repayment(self):
		"""还款流水推送"""
		data = excel_table_byname(self.file, 'repayment')
		param = json.loads(data[0]['param'])
		repayment_plan_list = self.r.get("jfx_6_periods_repayment_plan")
		success_amount = 0.00
		period = 1
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=self.r.get("jfx_6_periods_projectId"), environment=self.env, period=period,
			repayment_plan_type=1)
		repayment_detail_list = []
		for i in json.loads(repayment_plan_list):
			if i['period'] == period:
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
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"projectId": self.r.get("jfx_6_periods_projectId"),
				"sourceProjectId": self.r.get("jfx_6_periods_sourceProjectId"),
				"sourceUserId": self.r.get("jfx_6_periods_sourceUserId"),
				"serviceSn": Common.get_random("serviceSn"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
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
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			environment=self.env,
			product="cloudloan"
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("1")
	# @unittest.skipUnless(sys.argv[4] == "early_repayment", "条件成立时执行")
	def test_113_repayment(self):
		"""还款流水推送:提前全部结清"""
		data = excel_table_byname(self.file, 'repayment')
		param = json.loads(data[0]['param'])
		for per in range(1, 7):
			success_amount = GetSqlData.get_repayment_amount(
				project_id=self.r.get("jfx_6_periods_projectId"),
				environment=self.env,
				period=per
			)
			param.update(
				{
					"projectId": self.r.get('jfx_6_periods_projectId'),
					"transactionId": self.r.get('jfx_6_periods_transactionId'),
					"sourceProjectId": self.r.get('jfx_6_periods_sourceProjectId'),
					"sourcePlanId": Common.get_random('sourceProjectId'),
					"sourceRepaymentId": Common.get_random("transactionId"),
					"planPayDate": Common.get_repaydate(6)[per - 1],
					"payTime": Common.get_time('-'),
					"successAmount": float(success_amount),
					"period": per
				}
			)
			for i in range(len(param['repaymentDetailList'])):
				pay_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get('jfx_6_periods_projectId'),
					environment=self.env,
					period=per,
					repayment_plan_type=param['repaymentDetailList'][i]['planCategory']
				)
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"payAmount": float(pay_detail.get("cur_amount"))
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
				environment=self.env,
				product="cloudloan"
			)

			self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "repayment", "条件成立时执行")
	@unittest.skip("11")
	def test_114_capital_flow(self):
		"""资金流水推送"""
		data = excel_table_byname(self.file, 'cash_push')
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			project_id=self.r.get("jfx_6_periods_projectId"),
			environment=self.env,
			period=1
		)
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"projectId": self.r.get("jfx_6_periods_projectId"),
				"sourceProjectId": self.r.get("jfx_6_periods_sourceProjectId"),
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
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			environment=self.env,
			product="cloudloan"
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	def test_115_apply_cancel(self):
		"""进件取消"""
		data = excel_table_byname(self.file, 'apply_cancel')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"projectId": self.r.get("jfx_6_periods_projectId"),
				"sourceProjectId": self.r.get("jfx_6_periods_sourceProjectId")
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

	@unittest.skip("-")
	def test_116_offline_partial(self):
		"""线下还款:部分还款"""
		data = excel_table_byname(self.file, 'offline_partial')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceRequestId": Common.get_random("requestNum"),
				"sourceRepaymentId": Common.get_random("requestNum"),
				"projectId": self.r.get("jfx_6_periods_projectId"),
				"sourceProjectId": self.r.get("jfx_6_periods_sourceProjectId"),
				"sourceUserId": self.r.get("jfx_6_periods_sourceUserId"),
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
			environment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))


if __name__ == '__main__':
	unittest.main()
