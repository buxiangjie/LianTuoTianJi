# -*- coding: UTF-8 -*-
"""
@auth:卜祥杰
@date:2020-06-23 14:51:00
@describe: 即分期医疗3期
"""
import unittest
import os
import json
import sys
import time
from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = Logger(logger="test_jfqyl_3_periods_tp").getlog()


class Jfqyl3Tp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = 'qa'
		cls.r = Common.conn_redis(environment=cls.env)
		file = Config().get_item('File', 'jfq_case_file')
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_apply(self):
		"""进件"""
		data = excel_table_byname(self.excel, 'apply')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('jfqyl_3_periods', self.env)
		self.r.mset(
			{
				"jfqyl_3_periods_sourceUserId": Common.get_random('userid'),
				"jfqyl_3_periods_transactionId": Common.get_random('transactionId'),
				"jfqyl_3_periods_phone": Common.get_random('phone'),
				"jfqyl_3_periods_sourceProjectId": Common.get_random('sourceProjectId'),
			}
		)
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('jfqyl_3_periods_sourceProjectId'),
				"sourceUserId": self.r.get('jfqyl_3_periods_sourceUserId'),
				"transactionId": self.r.get('jfqyl_3_periods_transactionId')
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time("-"),
				"applyAmount": 33333.33,
				"applyTerm": 3,
				"productCode": "FQ_JK_JFQYL"
			}
		)
		param['loanInfo'].update(
			{
				"loanAmount": 33333.33,
				"loanTerm": 3,
				"assetInterestRate": 0.153,
				"userInterestRate": 0.153
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('jfqyl_3_periods_cardNum'),
				"custName": self.r.get('jfqyl_3_periods_custName'),
				"phone": self.r.get('jfqyl_3_periods_phone')
			}
		)
		param["cardInfo"]["accountProp"] = 1
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="gateway",
			environment=self.env
		)
		self.r.set('jfqyl_3_periods_projectId', rep['content']['projectId'])
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	def test_101_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'jfq_sign_credit.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfqyl_3_periods_sourceUserId'),
				"contractType": 5,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('jfqyl_3_periods_transactionId'),
				"associationId": self.r.get('jfqyl_3_periods_projectId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_102_query_apply_result(self):
		"""进件结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('jfqyl_3_periods_projectId'),
			environment=self.env
		)
		data = excel_table_byname(self.excel, 'query_apply_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('jfqyl_3_periods_sourceProjectId'),
				"projectId": self.r.get('jfqyl_3_periods_projectId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))
		self.assertEqual(json.loads(rep.text)['content']['auditStatus'], 2)

	# @unittest.skip("_")
	def test_103_sign_borrow(self):
		"""上传借款协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'jfq_sign_borrow.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('jfqyl_3_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('jfqyl_3_periods_transactionId'),
				"associationId": self.r.get('jfqyl_3_periods_projectId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.r.set("jfqyl_3_periods_contractId", json.loads(rep.text)['content']['contractId'])
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	def test_105_image_upload(self):
		"""上传图片"""
		data = excel_table_byname(self.excel, 'image_upload')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"associationId": self.r.get('jfqyl_3_periods_projectId')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	# @unittest.skip("-")
	def test_106_contact_query(self):
		"""合同结果查询:获取签章后的借款协议"""
		data = excel_table_byname(self.excel, 'contract_query')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"associationId": self.r.get('jfqyl_3_periods_projectId'),
				"serviceSn": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": self.r.get("jfqyl_3_periods_sourceUserId"),
				"contractId": self.r.get("jfqyl_3_periods_contractId")
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_107_calculate(self):
		"""还款计划试算（未放款）:正常还款"""
		data = excel_table_byname(self.excel, 'calculate')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("jfqyl_3_periods_sourceUserId"),
				"transactionId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"projectId": self.r.get("jfqyl_3_periods_projectId")
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_108_loan_pfa(self):
		"""放款申请"""
		data = excel_table_byname(self.excel, 'loan_pfa')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		self.r.set("jfqyl_3_periods_loan_serviceSn", Common.get_random("serviceSn"))
		param.update(
			{
				"sourceProjectId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"projectId": self.r.get("jfqyl_3_periods_projectId"),
				"sourceUserId": self.r.get("jfqyl_3_periods_sourceUserId"),
				"serviceSn": self.r.get("jfqyl_3_periods_loan_serviceSn"),
				"id": self.r.get('jfqyl_3_periods_cardNum'),
				"accountName": self.r.get("jfqyl_3_periods_custName"),
				"amount": 33333.33,
				"accountProp": 1,
				"idType": 10,
				"openAccountProvince": "110000",
				"openAccountCity": "110100",
				"openAccountBankNameSub": "招商银行上地支行"
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))
		# 修改支付表中的品钛返回code
		time.sleep(8)
		GetSqlData.change_pay_status(
			environment=self.env,
			project_id=self.r.get('jfqyl_3_periods_projectId')
		)

	def test_109_loan_query(self):
		"""放款结果查询"""
		GetSqlData.loan_set(environment=self.env, project_id=self.r.get('jfqyl_3_periods_projectId'))
		data = excel_table_byname(self.excel, 'pfa_query')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": self.r.get("jfqyl_3_periods_loan_serviceSn")})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))
		self.assertEqual(json.loads(rep.text)['content']['projectLoanStatus'], 3)

	def test_110_query_repayment_plan(self):
		"""国投云贷还款计划查询"""
		data = excel_table_byname(self.excel, 'query_repayment_plan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"transactionId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"projectId": self.r.get("jfqyl_3_periods_projectId")
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.r.set("jfqyl_3_periods_repayment_plan", json.dumps(json.loads(rep.text)['content']['repaymentPlanList']))
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "early_settlement", "-")
	# @unittest.skip("跳过")
	def test_111_calculate(self):
		"""还款计划试算:提前结清"""
		data = excel_table_byname(self.excel, 'calculate')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("jfqyl_3_periods_sourceUserId"),
				"transactionId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"projectId": self.r.get("jfqyl_3_periods_projectId"),
				"businessType": 2
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.r.set(
			"jfqyl_3_periods_early_settlement_repayment_plan",
			json.dumps(json.loads(rep.text)['content']['repaymentPlanList'])
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "early_settlement", "-")
	# @unittest.skip("跳过")
	def test_112_calculate(self):
		"""还款计划试算:退货"""
		data = excel_table_byname(self.excel, 'calculate')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("jfqyl_3_periods_sourceUserId"),
				"transactionId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"projectId": self.r.get("jfqyl_3_periods_projectId"),
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.r.set(
			"jfqyl_3_periods_return_repayment_plan",
			json.dumps(json.loads(rep.text)['content']['repaymentPlanList'])
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "repayment_offline", "-")
	@unittest.skip("跳过")
	def test_113_offline_repay_repayment(self):
		"""线下还款流水推送：正常还一期"""
		data = excel_table_byname(self.excel, 'offline_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=self.r.get("jfqyl_3_periods_projectId"),
			environment=self.env,
			period=period,
			repayment_plan_type=1
		)
		repayment_plan_list = self.r.get("jfqyl_3_periods_repayment_plan")
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
				"projectId": self.r.get("jfqyl_3_periods_projectId"),
				"transactionId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "early_settlement_offline", "-")
	@unittest.skip("跳过")
	def test_114_offline_nrepay_early_settlement(self):
		"""线下还款流水推送：提前全部结清"""
		data = excel_table_byname(self.excel, 'offline_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=self.r.get("jfqyl_3_periods_projectId"),
			environment=self.env,
			period=1,
			repayment_plan_type=1
		)
		repayment_plan_list = json.loads(self.r.get("jfqyl_3_periods_early_settlement_repayment_plan"))
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
				"projectId": self.r.get("jfqyl_3_periods_projectId"),
				"transactionId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	def test_116_return(self):
		"""退货"""
		data = excel_table_byname(self.excel, 'offline_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=self.r.get("jfqyl_3_periods_projectId"),
			environment=self.env,
			period=1,
			repayment_plan_type=1
		)
		repayment_plan_list = json.loads(self.r.get("jfqyl_3_periods_return_repayment_plan"))
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
				"projectId": self.r.get("jfqyl_3_periods_projectId"),
				"transactionId": self.r.get("jfqyl_3_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("jfqyl_3_periods_sourceProjectId"),
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	def test_117_capital_flow(self):
		"""资金流水推送"""
		data = excel_table_byname(self.excel, 'cash_push')
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			project_id=self.r.get("jfqyl_3_periods_projectId"),
			environment=self.env,
			period=1
		)
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"projectId": self.r.get("jfqyl_3_periods_projectId"),
				"sourceProjectId": self.r.get("jfqyl_3_periods_sourceProjectId"),
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
		response_data = json.loads(Common.dencrypt_response(rep.text))
		self.assertEqual(response_data['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	def test_118_project_cancel(self):
		"""进件取消"""
		data = excel_table_byname(self.excel, 'project_cancel')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"projectId": self.r.get("jfqyl_3_periods_projectId"),
				"sourceProjectId": self.r.get("jfqyl_3_periods_sourceProjectId")
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
