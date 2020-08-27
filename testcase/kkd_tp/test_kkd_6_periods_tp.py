# -*- coding: UTF-8 -*-
"""
@auth:卜祥杰
@date:2020-05-12 11:26:00
@describe: 卡卡贷6期
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

logger = Logger(logger="test_kkd_6_periods_tp").getlog()


class Kkd6Tp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = sys.argv[3]
		cls.r = Common.conn_redis(enviroment=cls.env)
		file = Config().get_item('File', 'kkd_case_file')
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_apply(self):
		"""进件"""
		data = excel_table_byname(self.excel, 'apply')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('kkd_6_periods', self.env)
		self.r.mset(
			{
				"kkd_6_periods_sourceUserId": Common.get_random('userid'),
				"kkd_6_periods_transactionId": Common.get_random('transactionId'),
				"kkd_6_periods_phone": Common.get_random('phone'),
				"kkd_6_periods_sourceProjectId": Common.get_random('sourceProjectId'),
			}
		)
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('kkd_6_periods_sourceProjectId'),
				"sourceUserId": self.r.get('kkd_6_periods_sourceUserId'),
				"transactionId": self.r.get('kkd_6_periods_transactionId')
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('kkd_6_periods_cardNum'),
				"custName": self.r.get('kkd_6_periods_custName'),
				"phone": self.r.get('kkd_6_periods_phone')
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time("-"),
				"productCode": "XJ_WX_KKD",
				"applyTerm": 6
			}
		)
		param['loanInfo'].update({"loanTerm": 6})
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
		projectId = json.loads(rep.text)['content']['projectId']
		self.r.set('kkd_6_periods_projectId', projectId)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_101_sign_credit(self):
		"""上传授信协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'kkd_sign_credit.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('kkd_6_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('kkd_6_periods_transactionId'),
				"associationId": self.r.get('kkd_6_periods_projectId')
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

	def test_102_query_apply_result(self):
		"""进件结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('kkd_6_periods_projectId'),
			enviroment=self.env
		)
		data = excel_table_byname(self.excel, 'query_apply_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('kkd_6_periods_sourceProjectId'),
				"projectId": self.r.get('kkd_6_periods_projectId')
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
		self.assertEqual(json.loads(rep.text)['content']['auditStatus'], 2)

	def test_103_sign_borrow(self):
		"""上传借款协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'kkd_sign_borrow.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('kkd_6_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('kkd_6_periods_transactionId'),
				"associationId": self.r.get('kkd_6_periods_projectId')
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
		self.r.set("kkd_6_periods_contractId", json.loads(rep.text)['content']['contractId'])
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	def test_104_sign_guarantee(self):
		"""上传担保函"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'kkd_sign_guarantee.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('kkd_6_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('kkd_6_periods_transactionId'),
				"associationId": self.r.get('kkd_6_periods_projectId')
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

	def test_105_image_upload(self):
		"""上传风控相关图片"""
		data = excel_table_byname(self.excel, 'image_upload')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"associationId": self.r.get('kkd_6_periods_projectId')})
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

	def test_106_contact_query(self):
		"""合同结果查询:获取签章后的借款协议"""
		data = excel_table_byname(self.excel, 'contract_query')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"associationId": self.r.get('kkd_6_periods_projectId'),
				"serviceSn": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": self.r.get("kkd_6_periods_sourceUserId"),
				"contractId": self.r.get("kkd_6_periods_contractId")
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

	def test_107_calculate(self):
		"""还款计划试算（未放款）:正常还款"""
		data = excel_table_byname(self.excel, 'calculate')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("kkd_6_periods_sourceUserId"),
				"transactionId": self.r.get("kkd_6_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("kkd_6_periods_sourceProjectId"),
				"projectId": self.r.get("kkd_6_periods_projectId")
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

	def test_108_loan_pfa(self):
		"""放款申请"""
		data = excel_table_byname(self.excel, 'loan_pfa')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		self.r.set("kkd_6_periods_loan_serviceSn", Common.get_random("serviceSn"))
		param.update(
			{
				"sourceProjectId": self.r.get("kkd_6_periods_sourceProjectId"),
				"projectId": self.r.get("kkd_6_periods_projectId"),
				"sourceUserId": self.r.get("kkd_6_periods_sourceUserId"),
				"serviceSn": self.r.get("kkd_6_periods_loan_serviceSn"),
				"id": self.r.get('kkd_6_periods_cardNum'),
				"accountName": self.r.get('kkd_6_periods_custName')
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
		# 修改支付表中的品钛返回code
		time.sleep(8)
		GetSqlData.change_pay_status(
			enviroment=self.env,
			project_id=self.r.get('kkd_6_periods_projectId')
		)

	def test_109_loan_query(self):
		"""放款结果查询"""
		GetSqlData.loan_set(enviroment=self.env, project_id=self.r.get('kkd_6_periods_projectId'))
		data = excel_table_byname(self.excel, 'pfa_query')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": self.r.get("kkd_6_periods_loan_serviceSn")})
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
		self.assertEqual(json.loads(rep.text)['content']['projectLoanStatus'], 3)

	def test_110_query_repayment_plan(self):
		"""国投云贷还款计划查询"""
		data = excel_table_byname(self.excel, 'query_repayment_plan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"transactionId": self.r.get("kkd_6_periods_sourceProjectId"),
				"projectId": self.r.get("kkd_6_periods_projectId")
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
		self.r.set("kkd_6_periods_repayment_plan", json.dumps(json.loads(rep.text)['content']['repaymentPlanList']))
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	@unittest.skipUnless(sys.argv[4] == "repayment", "-")
	# @unittest.skip("跳过")
	def test_111_calculate(self):
		"""还款计划试算（已放款）:正常还款"""
		data = excel_table_byname(self.excel, 'calculate')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("kkd_6_periods_sourceUserId"),
				"transactionId": self.r.get("kkd_6_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("kkd_6_periods_sourceProjectId"),
				"projectId": self.r.get("kkd_6_periods_projectId")
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

	@unittest.skipUnless(sys.argv[4] == "early_settlement", "-")
	# @unittest.skip("跳过")
	def test_112_calculate(self):
		"""还款计划试算:提前结清"""
		data = excel_table_byname(self.excel, 'calculate')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": self.r.get("kkd_6_periods_sourceUserId"),
				"transactionId": self.r.get("kkd_6_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("kkd_6_periods_sourceProjectId"),
				"projectId": self.r.get("kkd_6_periods_projectId"),
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.r.set(
			"kkd_6_periods_early_settlement_repayment_plan",
			json.dumps(json.loads(rep.text)['content']['repaymentPlanList'])
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	@unittest.skipUnless(sys.argv[4] == "repayment_offline", "-")
	# @unittest.skip("跳过")
	def test_113_offline_repay_repayment(self):
		"""线下还款流水推送：正常还一期"""
		data = excel_table_byname(self.excel, 'offline_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=self.r.get("kkd_6_periods_projectId"),
			enviroment=self.env,
			period=period,
			repayment_plan_type=1
		)
		repayment_plan_list = self.r.get("kkd_6_periods_repayment_plan")
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
				"projectId": self.r.get("kkd_6_periods_projectId"),
				"transactionId": self.r.get("kkd_6_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("kkd_6_periods_sourceProjectId"),
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
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	@unittest.skipUnless(sys.argv[4] == "early_settlement_offline", "-")
	# @unittest.skip("跳过")
	def test_114_offline_repay_early_settlement(self):
		"""线下还款流水推送：提前全部结清"""
		data = excel_table_byname(self.excel, 'offline_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=self.r.get("kkd_6_periods_projectId"),
			enviroment=self.env,
			period=1,
			repayment_plan_type=1
		).get("plan_pay_date")
		repayment_plan_list = self.r.get("kkd_6_periods_early_settlement_repayment_plan")
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
				"projectId": self.r.get("kkd_6_periods_projectId"),
				"transactionId": self.r.get("kkd_6_periods_sourceProjectId"),
				"sourceProjectId": self.r.get("kkd_6_periods_sourceProjectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date),
				"successAmount": success_amount,
				"repayType": 2,
				"period": json.loads(repayment_plan_list)[0]['period'],
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	def test_115_debt_transfer(self):
		"""上传债转函"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'kkd_debt_transfer.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('kkd_6_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('kkd_6_periods_transactionId'),
				"associationId": self.r.get('kkd_6_periods_projectId')
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
		self.r.set("kkd_6_periods_contractId", json.loads(rep.text)['content']['contractId'])
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))


if __name__ == '__main__':
	unittest.main()
