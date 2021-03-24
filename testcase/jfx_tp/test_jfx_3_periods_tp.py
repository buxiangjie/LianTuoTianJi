# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date: 2019-08-13
@describe:金服侠-牙医贷一期3期产品流程用例
"""

import unittest
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.common_func import Common
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData



class Jfx3PeriodTp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = "qa"
		cls.r = Common.conn_redis(environment=cls.env)
		cls.file = Config().get_item('File', 'jfx_mul_case_file')

	@classmethod
	def tearDownClass(cls):
		pass

	def test_0_credit_apply(self):
		"""额度授信"""
		data = excel_table_byname(self.file, 'credit_apply_data')
		Common.p2p_get_userinfo('jfx_3_periods', self.env)
		self.r.mset(
			{
				"jfx_3_periods_sourceUserId": Common.get_random('userid'),
				'jfx_3_periods_transactionId': Common.get_random('transactionId'),
				"jfx_3_periods_phone": Common.get_random('phone'),
				"jfx_3_periods_firstCreditDate": Common.get_time()
			}
		)
		param = json.loads(data[0]['param'])
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('jfx_3_periods_cardNum'),
				"custName": self.r.get('jfx_3_periods_custName'),
				"phone": self.r.get('jfx_3_periods_phone')
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time()})
		param.update(
			{
				"sourceUserId": self.r.get('jfx_3_periods_sourceUserId'),
				"serviceSn": Common.get_random('serviceSn'),
				"transactionId": self.r.get('jfx_3_periods_transactionId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		headers["X-TBC-SKIP-SIGN"] = "true"
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="gateway",
			environment=self.env
		)
		self.r.mset(
			{
				"jfx_3_periods_creditId": rep['content']['creditId'],
				"jfx_3_periods_userId": rep['content']['userId']
			}
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	def test_1_query_result(self):
		"""授信结果查询"""
		GetSqlData.credit_set(
			environment=self.env,
			credit_id=self.r.get("jfx_3_periods_creditId")
		)
		data = excel_table_byname(self.file, 'credit_query_result')
		param = json.loads(data[0]['param'])
		param.update({"creditId": self.r.get('jfx_3_periods_creditId')})
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

	def test_2_query_user_amount(self):
		"""用户额度查询"""
		data = excel_table_byname(self.file, 'query_user_amount')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get('jfx_3_periods_sourceUserId'),
				"userId": self.r.get('jfx_3_periods_userId')
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

	def test_3_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'jfx_credit_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfx_3_periods_sourceUserId'),
				"contractType": 1,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('jfx_3_periods_transactionId'),
				"associationId": self.r.get('jfx_3_periods_creditId')
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

	def test_4_project_apply(self):
		"""进件"""
		data = excel_table_byname(self.file, 'test_project')
		param = json.loads(data[0]['param'])
		self.r.set('jfx_3_periods_sourceProjectId', Common.get_random('sourceProjectId'))
		param.update(
			{
				"sourceProjectId": self.r.get('jfx_3_periods_sourceProjectId'),
				"sourceUserId": self.r.get('jfx_3_periods_sourceUserId'),
				"transactionId": self.r.get('jfx_3_periods_transactionId')
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('jfx_3_periods_cardNum'),
				"custName": self.r.get('jfx_3_periods_custName'),
				"phone": self.r.get('jfx_3_periods_phone')
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time(),
				"applyTerm": 3,

			}
		)
		param['loanInfo'].update(
			{
				"loanTerm": 3
			}
		)
		param['cardInfo'].update(
			{
				"bankNameSub": "建设银行",
				"bankCode": 34,
				"bankCardNo": "6227002432220410613",
				"unifiedSocialCreditCode": Common.get_random("businessLicenseNo")
			}
		)
		self.r.set("jfx_3_periods_corporateAccountName", param['cardInfo']['corporateAccountName'])
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		headers["X-TBC-SKIP-SIGN"] = "true"
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="gateway",
			environment=self.env
		)
		self.r.set('jfx_3_periods_projectId', rep['content']['projectId'])
		self.assertEqual(int(data[0]['resultCode']), rep['resultCode'])

	def test_5_query_apply_result(self):
		"""进件结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('jfx_3_periods_projectId'),
			environment=self.env
		)
		data = excel_table_byname(self.file, 'project_query_apply_result')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('jfx_3_periods_sourceProjectId'),
				"projectId": self.r.get('jfx_3_periods_projectId')
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

	def test_51_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'jfx_credit_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfx_3_periods_sourceUserId'),
				"contractType": 5,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('jfx_3_periods_transactionId'),
				"associationId": self.r.get('jfx_3_periods_projectId')
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

	def test_6_contract_sign(self):
		"""上传借款合同"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'jfx_borrow_periods_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfx_3_periods_sourceUserId'),
				"contractType": 2,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('jfx_3_periods_transactionId'),
				"associationId": self.r.get('jfx_3_periods_projectId')
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

	def test_7_pfa(self):
		"""放款"""
		data = excel_table_byname(self.file, 'project_loan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('jfx_3_periods_sourceProjectId'),
				"projectId": self.r.get('jfx_3_periods_projectId'),
				"sourceUserId": self.r.get('jfx_3_periods_sourceUserId'),
				"serviceSn": Common.get_random('serviceSn'),
				"accountName": self.r.get("jfx_3_periods_corporateAccountName"),
				"bankCode": 34,
				"accountNo": "6227002432220410613"  # 6227003814170172872
			}
		)
		self.r.set("jfx_3_periods_pfa_serviceSn", param['serviceSn'])
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		headers["X-TBC-SKIP-SIGN"] = "true"
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="gateway",
			environment=self.env
		)
		self.assertEqual(int(data[0]['resultCode']), rep['resultCode'])
		GetSqlData.change_pay_status(
			environment=self.env,
			project_id=self.r.get('jfx_3_periods_projectId')
		)

	def test_8_pfa_query(self):
		"""放款结果查询"""
		GetSqlData.loan_set(
			environment=self.env,
			project_id=self.r.get('jfx_3_periods_projectId')
		)
		data = excel_table_byname(self.file, 'pfa_query')
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": self.r.get('jfx_3_periods_pfa_serviceSn')})
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

	def test_9_query_repaymentplan(self):
		"""还款计划查询"""
		data = excel_table_byname(self.file, 'repayment_plan')
		param = json.loads(data[0]['param'])
		param.update({"projectId": self.r.get('jfx_3_periods_projectId')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'], headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(int(data[0]['resultCode']), rep['resultCode'])
		self.r.set("jfx_3_periods_repayment_plan", json.dumps(rep['content']['repaymentPlanList']))

	# @unittest.skipUnless(sys.argv[4] == "repayment", "条件成立时执行")
	@unittest.skip("skip")
	def test_B_repayment(self):
		"""还款流水推送"""
		global plan_pay_date
		data = excel_table_byname(self.file, 'repayment')
		param = json.loads(data[0]['param'])
		repayment_plan_list = self.r.get("jfx_3_periods_repayment_plan")
		success_amount = 0.00
		repayment_detail_list = []
		period = 1
		for i in json.loads(repayment_plan_list):
			if i['period'] == period:
				plan_detail = {
					"sourceRepaymentDetailId": Common.get_random("transactionId"),
					"payAmount": i['restAmount'],
					"planCategory": i['repaymentPlanType']
				}
				success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
				plan_pay_date = i['planPayDate']
				repayment_detail_list.append(plan_detail)
		param.update(
			{
				"sourceRequestId": Common.get_random("requestNum"),
				"projectId": self.r.get("jfx_3_periods_projectId"),
				"sourceProjectId": self.r.get("jfx_3_periods_sourceProjectId"),
				"sourceUserId": self.r.get("jfx_3_periods_sourceUserId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"serviceSn": Common.get_random("serviceSn"),
				"payTime": Common.get_time("-"),
				"planPayDate": plan_pay_date,
				"successAmount": success_amount,
				"period": period
			}
		)
		param['repaymentDetailList'] = repayment_detail_list
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		headers["X-TBC-SKIP-SIGN"] = "true"
		rep = Common.response(
			faceaddr=data[0]['url'], headers=headers,
			data=param,
			environment=self.env,
			product="gateway"
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("1")
	# @unittest.skipUnless(sys.argv[4] == "early_repayment", "条件成立时执行")
	def test_B1_repayment(self):
		"""还款流水推送:提前全部结清"""
		data = excel_table_byname(self.file, 'repayment')
		param = json.loads(data[0]['param'])
		for per in range(1, 4):
			success_amount = GetSqlData.get_repayment_amount(
				project_id=self.r.get("jfx_3_periods_projectId"),
				environment=self.env,
				period=per)
			param.update(
				{
					"projectId": self.r.get('jfx_3_periods_projectId'),
					"transactionId": self.r.get('jfx_3_periods_transactionId'),
					"sourceProjectId": self.r.get('jfx_3_periods_sourceProjectId'),
					"sourcePlanId": Common.get_random('sourceProjectId'),
					"sourceRepaymentId": Common.get_random("transactionId"),
					"planPayDate": Common.get_repaydate(3)[per - 1],
					"payTime": Common.get_time('-'),
					"successAmount": float(success_amount),
					"period": per
				}
			)
			for i in range(len(param['repaymentDetailList'])):
				pay_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get('jfx_3_periods_projectId'),
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
				faceaddr=data[0]['url'], headers=headers,
				data=json.dumps(param, ensure_ascii=False),
				environment=self.env,
				product="cloudloan"
			)

			self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "repayment", "条件成立时执行")
	@unittest.skip("skip")
	def test_C_capital_flow(self):
		"""资金流水推送"""
		data = excel_table_byname(self.file, 'cash_push')
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			project_id=self.r.get("jfx_3_periods_projectId"),
			environment=self.env,
			period=1
		)
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"projectId": self.r.get("jfx_3_periods_projectId"),
				"sourceProjectId": self.r.get("jfx_3_periods_sourceProjectId"),
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
			faceaddr=data[0]['url'], headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			environment=self.env,
			product="cloudloan"
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("跳过")
	def test_D_offline_partial(self):
		"""线下还款:部分还款"""
		data = excel_table_byname(self.file, 'offline_partial')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceRequestId": Common.get_random("requestNum"),
				"sourceRepaymentId": Common.get_random("requestNum"),
				"projectId": self.r.get("jfx_3_periods_projectId"),
				"sourceProjectId": self.r.get("jfx_3_periods_sourceProjectId"),
				"sourceUserId": self.r.get("jfx_3_periods_sourceUserId"),
				"serviceSn": Common.get_random("serviceSn"),
				"payTime": Common.get_time("-"),
				"successAmount": 50,
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
