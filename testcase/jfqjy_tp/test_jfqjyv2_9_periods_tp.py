# -*- coding: UTF-8 -*-
"""
@auth:卜祥杰
@date:2020-09-21 15:50:00
@describe: 即分期教育V2 9期
"""
import unittest
import os
import json
import sys

from busi_assert.busi_asset import Assert
from common.common_func import Common
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class JfqjyV29Tp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = "qa"
		cls.r = Common.conn_redis(environment=cls.env)
		cls.file = Config().get_item('File', 'jfq_case_file')

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_apply(self):
		"""进件"""
		data = excel_table_byname(self.file, 'apply')
		Common.p2p_get_userinfo('jfqjyv2_9_periods', self.env)
		self.r.mset(
			{
				"jfqjyv2_9_periods_sourceUserId": Common.get_random('userid'),
				"jfqjyv2_9_periods_transactionId": Common.get_random('transactionId'),
				"jfqjyv2_9_periods_phone": Common.get_random('phone'),
				"jfqjyv2_9_periods_sourceProjectId": Common.get_random('sourceProjectId'),
			}
		)
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('jfqjyv2_9_periods_sourceProjectId'),
				"sourceUserId": self.r.get('jfqjyv2_9_periods_sourceUserId'),
				"transactionId": self.r.get('jfqjyv2_9_periods_transactionId')
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time("-"),
				"applyAmount": 33333.33,
				"applyTerm": 9,
				"productCode": "FQ_JK_JFQJYV2"
			}
		)
		param['loanInfo'].update(
			{
				"loanAmount": 33333.33,
				"loanTerm": 9,
				"assetInterestRate": 0.154,
				"userInterestRate": 0.087010
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('jfqjyv2_9_periods_cardNum'),
				"custName": self.r.get('jfqjyv2_9_periods_custName'),
				"phone": self.r.get('jfqjyv2_9_periods_phone')
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
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
		self.r.set('jfqjyv2_9_periods_projectId', rep['content']['projectId'])
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	def test_101_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfqjyv2_9_periods_sourceUserId'),
				"contractType": 5,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('jfqjyv2_9_periods_transactionId'),
				"associationId": self.r.get('jfqjyv2_9_periods_projectId'),
				"content": Common.get_json_data('data', 'credit_sign.json').get("content")
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

	def test_102_query_apply_result(self):
		"""进件结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('jfqjyv2_9_periods_projectId'),
			environment=self.env
		)
		data = excel_table_byname(self.file, 'query_apply_result')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('jfqjyv2_9_periods_sourceProjectId'),
				"projectId": self.r.get('jfqjyv2_9_periods_projectId')
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
		self.assertEqual(rep['content']['auditStatus'], 2)

	def test_103_sign_borrow(self):
		"""上传借款协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfqjyv2_9_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"contractType": 2,
				"transactionId": self.r.get('jfqjyv2_9_periods_transactionId'),
				"associationId": self.r.get('jfqjyv2_9_periods_projectId'),
				"content": Common.get_json_data('data', 'borrow_sign.json').get("content")
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
		self.r.set("jfqjyv2_9_periods_contractId", rep['content']['contractId'])
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	def test_105_image_upload(self):
		"""上传图片"""
		data = excel_table_byname(self.file, 'image_upload')
		param = json.loads(data[0]['param'])
		param.update({"associationId": self.r.get('jfqjyv2_9_periods_projectId')})
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

	def test_106_contact_query(self):
		"""合同结果查询:获取签章后的借款协议"""
		data = excel_table_byname(self.file, 'contract_query')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"associationId": self.r.get('jfqjyv2_9_periods_projectId'),
				"serviceSn": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": self.r.get("jfqjyv2_9_periods_sourceUserId"),
				"contractId": self.r.get("jfqjyv2_9_periods_contractId")
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

	def test_107_calculate(self):
		"""还款计划试算（未放款）:正常还款"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("jfqjyv2_9_periods_sourceUserId"),
				"transactionId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"projectId": self.r.get("jfqjyv2_9_periods_projectId")
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

	def test_108_loan_pfa(self):
		"""放款申请"""
		data = excel_table_byname(self.file, 'loan_pfa')
		param = json.loads(data[0]['param'])
		self.r.set("jfqjyv2_9_periods_loan_serviceSn", Common.get_random("serviceSn"))
		param.update(
			{
				"sourceProjectId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"projectId": self.r.get("jfqjyv2_9_periods_projectId"),
				"sourceUserId": self.r.get("jfqjyv2_9_periods_sourceUserId"),
				"serviceSn": self.r.get("jfqjyv2_9_periods_loan_serviceSn"),
				"id": self.r.get('jfqjyv2_9_periods_cardNum'),
				"accountName": self.r.get("jfqjyv2_9_periods_custName"),
				"amount": 33333.33
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
		# 修改支付表中的品钛返回code
		GetSqlData.change_pay_status(
			environment=self.env,
			project_id=self.r.get('jfqjyv2_9_periods_projectId')
		)

	def test_109_loan_query(self):
		"""放款结果查询"""
		GetSqlData.loan_set(environment=self.env, project_id=self.r.get('jfqjyv2_9_periods_projectId'))
		data = excel_table_byname(self.file, 'pfa_query')
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": self.r.get("jfqjyv2_9_periods_loan_serviceSn")})
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
		self.assertEqual(rep['content']['projectLoanStatus'], 3)

	def test_110_query_repayment_plan(self):
		"""国投云贷还款计划查询"""
		data = excel_table_byname(self.file, 'query_repayment_plan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"transactionId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"projectId": self.r.get("jfqjyv2_9_periods_projectId")
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
		Assert.check_repayment(False, self.env, self.r.get("jfqjyv2_9_periods_projectId"))
		self.r.set("jfqjyv2_9_periods_repayment_plan", json.dumps(rep['content']['repaymentPlanList']))

	# @unittest.skip("跳过")
	def test_111_calculate(self):
		"""还款计划试算:提前结清"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("jfqjyv2_9_periods_sourceUserId"),
				"transactionId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"projectId": self.r.get("jfqjyv2_9_periods_projectId"),
				"businessType": 2,
				"repayTime": Common.get_time("-")
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
		self.r.set(
			"jfqjyv2_9_periods_early_settlement_repayment_plan",
			json.dumps(rep['content']['repaymentPlanList'])
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("即科不支持退货")
	def test_112_calculate(self):
		"""还款计划试算:退货"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("jfqjyv2_9_periods_sourceUserId"),
				"transactionId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"projectId": self.r.get("jfqjyv2_9_periods_projectId"),
				"businessType": 3
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

	@unittest.skip("跳过")
	def test_113_offline_repay_repayment(self):
		"""线下还款流水推送：正常还一期"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		period = 1
		plan_pay_date = GetSqlData.get_repayment_plan_date(
			project_id=self.r.get("jfqjyv2_9_periods_projectId"),
			environment=self.env,
			repayment_plan_type=1,
			period=period
		)
		repayment_plan_list = self.r.get("jfqjyv2_9_periods_repayment_plan")
		success_amount = 0.00
		repayment_detail_list = []
		for i in json.loads(repayment_plan_list):
			if i['period'] == period:
				plan_detail = {
					"sourceRepaymentDetailId": Common.get_random("transactionId"),
					"payAmount": i['restAmount'],
					"planCategory": i['repaymentPlanType']
				}
				success_amount = round(success_amount + float(plan_detail.get("payAmount")), 2)
				repayment_detail_list.append(plan_detail)
		param.update(
			{
				"projectId": self.r.get("jfqjyv2_9_periods_projectId"),
				"transactionId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": plan_pay_date['plan_pay_date'],
				"successAmount": success_amount,
				"payTime": Common.get_time("-"),
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
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))
		Assert.check_repayment(True, self.env, self.r.get("jfqjyv2_9_periods_projectId"), param)

	@unittest.skip("跳过")
	def test_114_offline_nrepay_early_settlement(self):
		"""线下还款流水推送：提前全部结清"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_plan_date(
			project_id=self.r.get("jfqjyv2_9_periods_projectId"),
			environment=self.env,
			repayment_plan_type=1,
			period=1
		)
		repayment_plan_list = json.loads(self.r.get("jfqjyv2_9_periods_early_settlement_repayment_plan"))
		success_amount = 0.00
		repayment_detail_list = []
		for i in repayment_plan_list:
			plan_detail = {
				"sourceRepaymentDetailId": Common.get_random("transactionId"),
				"payAmount": i['amount'],
				"planCategory": i['repaymentPlanType']
			}
			success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
			repayment_detail_list.append(plan_detail)
		param.update(
			{
				"projectId": self.r.get("jfqjyv2_9_periods_projectId"),
				"transactionId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": plan_pay_date['plan_pay_date'],
				"successAmount": success_amount,
				"repayType": 2,
				"period": repayment_plan_list[0]['period'],
				"payTime": Common.get_time("-")
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
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))
		Assert.check_repayment(True, self.env, self.r.get("jfqjyv2_9_periods_projectId"), param)

	@unittest.skip("-")
	def test_115_debt_transfer(self):
		"""上传债转函"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'kkd_debt_transfer.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfqjyv2_9_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('jfqjyv2_9_periods_transactionId'),
				"associationId": self.r.get('jfqjyv2_9_periods_projectId')
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
		self.r.set("jfqjyv2_9_periods_contractId", rep['content']['contractId'])
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	def test_116_return(self):
		"""退货"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_plan_date(
			project_id=self.r.get("jfqjyv2_9_periods_projectId"),
			environment=self.env,
			repayment_plan_type=1,
			period=1
		)
		repayment_plan_list = json.loads(self.r.get("jfqjyv2_9_periods_return_repayment_plan"))
		success_amount = 0.00
		repayment_detail_list = []
		for i in repayment_plan_list:
			plan_detail = {
				"sourceRepaymentDetailId": Common.get_random("transactionId"),
				"payAmount": i['amount'],
				"planCategory": i['repaymentPlanType']
			}
			success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
			repayment_detail_list.append(plan_detail)
		param.update(
			{
				"projectId": self.r.get("jfqjyv2_9_periods_projectId"),
				"transactionId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
				"successAmount": success_amount,
				"repayType": 3,
				"period": repayment_plan_list[0]['period'],
				"payTime": Common.get_time("-")
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
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))
		Assert.check_repayment(True, self.env, self.r.get("jfqjyv2_9_periods_projectId"), param)

	@unittest.skip("-")
	def test_117_capital_flow(self):
		"""资金流水推送"""
		data = excel_table_byname(self.file, 'cash_push')
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			project_id=self.r.get("jfqjyv2_9_periods_projectId"),
			environment=self.env,
			period=1
		)
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"projectId": self.r.get("jfqjyv2_9_periods_projectId"),
				"sourceProjectId": self.r.get("jfqjyv2_9_periods_sourceProjectId"),
				"repaymentPlanId": Common.get_random("sourceProjectId"),
				"sucessAmount": success_amount,
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
			product="gateway"
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))


if __name__ == '__main__':
	unittest.main()
