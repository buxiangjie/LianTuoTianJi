# -*- coding: UTF-8 -*-
"""
@auth:卜祥杰
@date:2019-10-22 09:39:00
@describe: 任买医美十二期进件-放款流程
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

logger = Logger(logger="test_rmkj_12_periods_tp").getlog()


class Rmkj12Tp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = "qa"
		cls.r = Common.conn_redis(enviroment=cls.env)
		file = Config().get_item('File', 'rmkj_case_file')
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_apply(self):
		"""进件"""
		data = excel_table_byname(self.excel, 'apply')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('rmkj_12_periods', self.env)
		self.r.mset(
			{
				"rmkj_12_periods_sourceUserId": Common.get_random('userid'),
				"rmkj_12_periods_transactionId": Common.get_random('transactionId'),
				"rmkj_12_periods_phone": Common.get_random('phone'),
				"rmkj_12_periods_sourceProjectId": Common.get_random('sourceProjectId')
			}
		)
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('rmkj_12_periods_sourceProjectId'),
				"sourceUserId": self.r.get('rmkj_12_periods_sourceUserId'),
				"transactionId": self.r.get('rmkj_12_periods_transactionId')
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('rmkj_12_periods_cardNum'),
				"custName": self.r.get('rmkj_12_periods_custName'),
				"phone": self.r.get('rmkj_12_periods_phone')
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time("-"),
				"applyTerm": 12
			}
		)
		param['loanInfo'].update(
			{
				"loanTerm": 12
			}
		)
		param['cardInfo'].update({"unifiedSocialCreditCode": Common.get_random("businessLicenseNo")})
		param['bindingCardInfo'].update(
			{
				"bankCardNo": self.r.get('rmkj_12_periods_bankcard'),
				"bankPhone": self.r.get('rmkj_12_periods_phone'),
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
		self.r.set('rmkj_12_periods_projectId', rep['content']['projectId'])
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	def test_101_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'rmkj_sign_credit.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('rmkj_12_periods_sourceUserId'),
				"contractType": 5,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('rmkj_12_periods_transactionId'),
				"associationId": self.r.get('rmkj_12_periods_projectId')
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
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	def test_102_query_apply_result(self):
		"""进件结果查询"""
		time.sleep(4)
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('rmkj_12_periods_projectId'),
			enviroment=self.env
		)
		data = excel_table_byname(self.excel, 'query_apply_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('rmkj_12_periods_sourceProjectId'),
				"projectId": self.r.get('rmkj_12_periods_projectId')
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
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))
		self.assertEqual(rep['content']['auditStatus'], 2)

	def test_103_sign_borrow(self):
		"""上传借款协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'rmkj_sign_borrow.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('rmkj_12_periods_sourceUserId'),
				"contractType": 2,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('rmkj_12_periods_transactionId'),
				"associationId": self.r.get('rmkj_12_periods_projectId')
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
		self.r.set("rmkj_12_periods_contractId", rep['content']['contractId'])
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	def test_104_image_upload(self):
		"""上传医疗美容图片"""
		data = excel_table_byname(self.excel, 'image_upload')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"associationId": self.r.get('rmkj_12_periods_projectId')})
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
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	def test_105_contact_query(self):
		"""合同结果查询:获取签章后的借款协议"""
		data = excel_table_byname(self.excel, 'contract_query')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"associationId": self.r.get('rmkj_12_periods_projectId'),
				"serviceSn": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
				"contractId": self.r.get("rmkj_12_periods_contractId")
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
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	# def test_106_sign(self):
	# 	"""预签约"""
	# 	data = excel_table_byname(self.excel, 'sign')
	# 	print("接口名称:%s" % data[0]['casename'])
	# 	param = json.loads(data[0]['param'])
	# 	param.update(
	# 		{
	# 			"requestId": Common.get_random("serviceSn"),
	# 			"requestTime": Common.get_time("-"),
	# 			"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
	# 			"name": self.r.get("rmkj_12_periods_custName"),
	# 			"cardNo": self.r.get("rmkj_12_periods_cardNum"),
	# 			"bankNo": self.r.get("rmkj_12_periods_bankcard"),
	# 			"mobile": self.r.get("rmkj_12_periods_phone")
	# 		}
	# 	)
	# 	if len(data[0]['headers']) == 0:
	# 		headers = None
	# 	else:
	# 		headers = json.loads(data[0]['headers'])
	# 	rep = Common.response(
	# 		faceaddr=data[0]['url'],
	# 		headers=headers,
	# 		data=json.dumps(param, ensure_ascii=False),
	# 		product='pay',
	# 		enviroment=self.env
	# 	)
	# 	self.r.set("rmkj_12_periods_signTaskId", rep['data']['signTaskId'])
	# 	self.assertEqual(rep['code'], int(data[0]['resultCode']))
	#
	# def test_107_confirm(self):
	# 	"""确认签约"""
	# 	data = excel_table_byname(self.excel, 'confirm')
	# 	print("接口名称:%s" % data[0]['casename'])
	# 	param = Common.get_json_data("data", "rmkj_confirm.json")
	# 	param.update(
	# 		{
	# 			"requestId": Common.get_random("serviceSn"),
	# 			"requestTime": Common.get_time("-"),
	# 			"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
	# 			"signTaskId": self.r.get("rmkj_12_periods_signTaskId"),
	# 			"smsCode": "849201"
	# 		}
	# 	)
	# 	if len(data[0]['headers']) == 0:
	# 		headers = None
	# 	else:
	# 		headers = json.loads(data[0]['headers'])
	# 	rep = Common.response(
	# 		faceaddr=data[0]['url'],
	# 		headers=headers,
	# 		data=json.dumps(param, ensure_ascii=False),
	# 		product='pay',
	# 		enviroment=self.env
	# 	)
	# 	self.assertEqual(rep['code'], int(data[0]['resultCode']))
	# 	self.assertEqual(rep['data']['status'], 3)
	#
	# def test_108_query_sign(self):
	# 	"""绑卡结果查询"""
	# 	data = excel_table_byname(self.excel, 'query_sign')
	# 	print("接口名称:%s" % data[0]['casename'])
	# 	param = json.loads(data[0]['param'])
	# 	param.update(
	# 		{
	# 			"requestId": Common.get_random("serviceSn"),
	# 			"requestTime": Common.get_time("-"),
	# 			"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
	# 			"signTaskId": self.r.get("rmkj_12_periods_signTaskId")
	# 		}
	# 	)
	# 	if len(data[0]['headers']) == 0:
	# 		headers = None
	# 	else:
	# 		headers = json.loads(data[0]['headers'])
	# 	rep = Common.response(
	# 		faceaddr=data[0]['url'],
	# 		headers=headers,
	# 		data=json.dumps(param, ensure_ascii=False),
	# 		product='pay',
	# 		enviroment=self.env
	# 	)
	# 	self.assertEqual(rep['code'], int(data[0]['resultCode']))
	# 	self.assertEqual(rep['data']['status'], 3)
	#
	# def test_109_card_change(self):
	# 	"""还款卡推送"""
	# 	data = excel_table_byname(self.excel, 'card_change')
	# 	print("接口名称:%s" % data[0]['casename'])
	# 	param = json.loads(data[0]['param'])
	# 	param.update(
	# 		{
	# 			"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
	# 			"sourceProjectId": self.r.get("rmkj_12_periods_sourceProjectId"),
	# 			"projectId": self.r.get("rmkj_12_periods_projectId"),
	# 			"name": self.r.get("rmkj_12_periods_custName"),
	# 			"cardNo": self.r.get("rmkj_12_periods_cardNum"),
	# 			"mobile": self.r.get("rmkj_12_periods_phone"),
	# 			# "bankNo": self.r.get("rmkj_12_periods_bankcard"),
	# 			"bankNo": "6217002200003225702",
	# 			"businessType": 2
	# 		}
	# 	)
	# 	if len(data[0]['headers']) == 0:
	# 		headers = None
	# 	else:
	# 		headers = json.loads(data[0]['headers'])
	# 	rep = Common.response(
	# 		faceaddr=data[0]['url'],
	# 		headers=headers,
	# 		data=json.dumps(param, ensure_ascii=False),
	# 		product="cloudloan",
	# 		enviroment=self.env
	# 	)
	# 	self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	# @unittest.skip("-")
	def test_1099_deduction_share_sign(self):
		"""协议支付号共享"""
		data = excel_table_byname(self.excel, 'deduction_share_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
				"transactionId": Common.get_random("transactionId"),
				"sourceProjectId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"projectId": self.r.get("rmkj_12_periods_projectId"),
				"name": self.r.get("rmkj_12_periods_custName"),
				"cardNo": self.r.get("rmkj_12_periods_cardNum"),
				# "bankNo": "6217002200003225702",
				"bankNo": self.r.get("rmkj_12_periods_bankcard"),
				"bankPhone": self.r.get("rmkj_12_periods_phone"),
				"signNo": Common.get_random("businessLicenseNo"),
				"authLetterNo": Common.get_random("transactionId")

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
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	def test_110_loan_pfa(self):
		"""放款申请"""
		data = excel_table_byname(self.excel, 'loan_pfa')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		self.r.set("rmkj_12_periods_loan_serviceSn", Common.get_random("serviceSn"))
		param.update(
			{
				"sourceProjectId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"projectId": self.r.get("rmkj_12_periods_projectId"),
				"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
				"serviceSn": self.r.get("rmkj_12_periods_loan_serviceSn")
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
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))
		# 修改支付表中的品钛返回code
		time.sleep(8)
		GetSqlData.change_pay_status(
			enviroment=self.env,
			project_id=self.r.get('rmkj_12_periods_projectId')
		)

	def test_111_loan_query(self):
		"""放款结果查询"""
		GetSqlData.loan_set(enviroment=self.env, project_id=self.r.get('rmkj_12_periods_projectId'))
		data = excel_table_byname(self.excel, 'pfa_query')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": self.r.get("rmkj_12_periods_loan_serviceSn")})
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
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))
		self.assertEqual(rep['content']['projectLoanStatus'], 3)

	def test_112_query_repayment_plan(self):
		"""国投云贷还款计划查询"""
		data = excel_table_byname(self.excel, 'query_repayment_plan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"transactionId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"projectId": self.r.get("rmkj_12_periods_projectId")
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
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))
		self.r.set("rmkj_12_periods_repayment_plan", json.dumps(rep['content']['repaymentPlanList']))

	# @unittest.skipUnless(sys.argv[4] == "early_settlement", "-")
	# @unittest.skip("跳过")
	def test_114_early_settlement(self):
		"""还款计划试算:提前结清"""
		data = excel_table_byname(self.excel, 'calculate')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
				"transactionId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"projectId": self.r.get("rmkj_12_periods_projectId"),
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
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=self.env
		)
		self.r.set(
			"rmkj_12_periods_early_settlement_repayment_plan",
			json.dumps(rep['content']['repaymentPlanList'])
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "refunds", "-")
	# @unittest.skip("跳过")
	def test_115_calculate_refunds(self):
		"""还款计划试算:退货"""
		data = excel_table_byname(self.excel, 'calculate')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
				"transactionId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"projectId": self.r.get("rmkj_12_periods_projectId"),
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
			enviroment=self.env
		)
		self.r.set(
			"rmkj_12_periods_refunds_repayment_plan",
			json.dumps(rep['content']['repaymentPlanList'])
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "repayment", "-")
	@unittest.skip("跳过")
	def test_116_deduction_apply(self):
		"""主动还款:正常还一期"""
		data = excel_table_byname(self.excel, 'deduction_apply')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		repayment_plan_list = self.r.get("rmkj_12_periods_repayment_plan")
		success_amount = 0.00
		repayment_detail_list = []
		period = 1
		for i in json.loads(repayment_plan_list):
			if i['period'] == period:
				plan_detail = {
					"period": period,
					"payAmount": i['restAmount'],
					"planCategory": i['repaymentPlanType']
				}
				success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
				repayment_detail_list.append(plan_detail)
		param.update(
			{
				"sourceRequestId": Common.get_random("requestNum"),
				"projectId": self.r.get("rmkj_12_periods_projectId"),
				"sourceProjectId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
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
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=self.env
		)
		self.r.set("rmkj_12_periods_deductionTaskId", rep['content']['deductionTaskId'])
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("跳过")
	# @unittest.skipUnless(sys.argv[4] == "all_periods", "-")
	def test_117_deduction_apply_all_periods(self):
		"""主动还款:连续还款整笔结清"""
		data = excel_table_byname(self.excel, 'deduction_apply')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		repayment_plan_list = self.r.get("rmkj_12_periods_repayment_plan")
		maturity = GetSqlData.get_maturity(
			project_id=self.r.get("rmkj_12_periods_projectId"),
			enviroment=self.env
		)
		for period in range(1, maturity + 1):
			success_amount = 0.00
			repayment_detail_list = []
			for i in json.loads(repayment_plan_list):
				if i['period'] == period:
					plan_detail = {
						"period": i['period'],
						"payAmount": i['restAmount'],
						"planCategory": i['repaymentPlanType']
					}
					success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
					repayment_detail_list.append(plan_detail)
			param.update(
				{
					"sourceRequestId": Common.get_random("requestNum"),
					"projectId": self.r.get("rmkj_12_periods_projectId"),
					"sourceProjectId": self.r.get("rmkj_12_periods_sourceProjectId"),
					"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
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
			rep = Common.response(
				faceaddr=data[0]['url'],
				headers=headers,
				data=json.dumps(param, ensure_ascii=False)
				, product="cloudloan",
				enviroment=self.env
			)


			self.r.set("rmkj_12_periods_deductionTaskId", rep['content']['deductionTaskId'])
			self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("跳过")
	# @unittest.skipUnless(sys.argv[4] == "early_settlement", "-")
	def test_118_deduction_early_settlement(self):
		"""主动还款:提前全部结清"""
		data = excel_table_byname(self.excel, 'deduction_apply')
		print("接口名称:%s" % data[0]['casename'] + ": 提前结清")
		param = json.loads(data[0]['param'])
		repayment_plan_list = self.r.get("rmkj_12_periods_early_settlement_repayment_plan")
		success_amount = 0.00
		repayment_detail_list = []
		for i in json.loads(repayment_plan_list):
			plan_detail = {
				"period": i['period'],
				"payAmount": i['amount'],
				"planCategory": i['repaymentPlanType']
			}
			success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
			repayment_detail_list.append(plan_detail)
		param.update(
			{
				"sourceRequestId": Common.get_random("requestNum"),
				"projectId": self.r.get("rmkj_12_periods_projectId"),
				"sourceProjectId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"sourceUserId": self.r.get("rmkj_12_periods_sourceUserId"),
				"serviceSn": Common.get_random("serviceSn"),
				"repayType": 2,
				"payTime": Common.get_time("-"),
				"successAmount": success_amount,
				"period": json.loads(repayment_plan_list)[0]['period']
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
			enviroment=self.env
		)
		self.r.set("rmkj_12_periods_deductionTaskId", rep['content']['deductionTaskId'])
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] in ("repayment", "early_settlement"), "-")
	@unittest.skip("跳过")
	def test_119_deduction_query(self):
		"""主动还款结果查询"""
		data = excel_table_byname(self.excel, 'deduction_query')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"deductionTaskId": self.r.get("rmkj_12_periods_deductionTaskId")})
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
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "repayment_offline", "-")
	@unittest.skip("跳过")
	def test_120_offline_repay_repayment(self):
		"""线下还款流水推送：正常还一期"""
		data = excel_table_byname(self.excel, 'offline_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=self.r.get("rmkj_12_periods_projectId"), enviroment=self.env, period=1,
			repayment_plan_type=1)
		repayment_plan_list = self.r.get("rmkj_12_periods_repayment_plan")
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
				repayment_detail_list.append(plan_detail)
		param.update(
			{
				"projectId": self.r.get("rmkj_12_periods_projectId"),
				"transactionId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
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
			product="cloudloan",
			enviroment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "early_settlement_offline", "-")
	@unittest.skip("跳过")
	def test_121_offline_repay_early_settlement(self):
		"""线下还款流水推送：提前全部结清"""
		data = excel_table_byname(self.excel, 'offline_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=self.r.get("rmkj_12_periods_projectId"), enviroment=self.env, period=1,
			repayment_plan_type=1)
		repayment_plan_list = self.r.get("rmkj_12_periods_early_settlement_repayment_plan")
		success_amount = 0.00
		repayment_detail_list = []
		for i in json.loads(repayment_plan_list):
			plan_detail = {
				"sourceRepaymentDetailId": Common.get_random("transactionId"),
				"payAmount": i['amount'],
				"planCategory": i['repaymentPlanType']
			}
			success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
			repayment_detail_list.append(plan_detail)
		param.update(
			{
				"projectId": self.r.get("rmkj_12_periods_projectId"),
				"transactionId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("rmkj_12_periods_sourceProjectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
				"successAmount": success_amount,
				"repayType": 2,
				"period": json.loads(repayment_plan_list)[0]['period']
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
			enviroment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	# @unittest.skipUnless(sys.argv[4] == "refunds", "-")
	@unittest.skip("跳过")
	def test_122_refunds(self):
		"""线下还款流水推送：退货"""
		data = excel_table_byname(self.excel, 'offline_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=self.r.get("rmkj_9_periods_projectId"), enviroment=self.env, period=1,
			repayment_plan_type=1)
		repayment_plan_list = self.r.get("rmkj_9_periods_refunds_repayment_plan")
		success_amount = 0.00
		repayment_detail_list = []
		for i in json.loads(repayment_plan_list):
			plan_detail = {
				"sourceRepaymentDetailId": Common.get_random("transactionId"),
				"payAmount": i['amount'],
				"planCategory": i['repaymentPlanType']
			}
			success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
			repayment_detail_list.append(plan_detail)
		param.update(
			{
				"projectId": self.r.get("rmkj_9_periods_projectId"),
				"transactionId": self.r.get("rmkj_9_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("rmkj_9_periods_sourceProjectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": plan_pay_date['plan_pay_date'],
				"successAmount": success_amount,
				"repayType": 3,
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
			enviroment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))


if __name__ == '__main__':
	unittest.main()
