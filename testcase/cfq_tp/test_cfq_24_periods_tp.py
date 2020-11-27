#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:
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

logger = Logger(logger="test_cfq_24_periods_tp").getlog()


class Cfq24PeriodsTp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = "test"
		cls.r = Common.conn_redis(environment=cls.env)
		file = Config().get_item('File', 'cfq_24_periods_case_file')
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_approved(self):
		"""橙分期进件同意接口"""
		data = excel_table_byname(self.excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		Common.p2p_get_userinfo(project="cfq_24_periods", environment=self.env)
		self.r.mset(
			{
				"cfq_24_periods_sourceProjectId": Common.get_random("sourceProjectId"),
				"cfq_24_periods_sourceUserId": Common.get_random("userid"),
				"cfq_24_periods_transactionId": "Apollo" + Common.get_random("transactionId"),
				"cfq_24_periods_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("cfq_24_periods_sourceProjectId"),
				"sourceUserId": self.r.get("cfq_24_periods_sourceUserId"),
				"transactionId": self.r.get("cfq_24_periods_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": self.r.get("cfq_24_periods_cardNum"),
				"custName": self.r.get("cfq_24_periods_custName"),
				"phone": self.r.get("cfq_24_periods_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": self.r.get("cfq_24_periods_phone")})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			environment=self.env,
			product="pintic"
		)
		self.r.set("cfq_24_periods_projectId", rep['content']['projectId'])
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))
		# 修改进件审核状态
		GetSqlData.change_project_audit_status(
			project_id=self.r.get("cfq_24_periods_projectId"),
			environment=self.env
		)

	def test_101_query_audit_status(self):
		"""橙分期进件审核结果查询"""
		data = excel_table_byname(self.excel, 'query_audit_status')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("cfq_24_periods_sourceProjectId"),
				"projectId": self.r.get("cfq_24_periods_projectId")
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		time.sleep(5)
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			environment=self.env,
			product="pintic"
		)
		print("返回信息:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	def test_102_loan_notice(self):
		"""橙分期放款通知接口"""
		data = excel_table_byname(self.excel, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("cfq_24_periods_sourceProjectId"),
				"sourceUserId": self.r.get("cfq_24_periods_sourceUserId"),
				"projectId": self.r.get("cfq_24_periods_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("cfq_24_periods_cardNum"),
				"bankPhone": self.r.get("cfq_24_periods_phone"),
				"loanTime": Common.get_time("-")
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
			product="pintic"
		)
		print("返回信息:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	def test_103_loanasset(self):
		"""橙分期进件放款同步接口"""
		global period
		data = excel_table_byname(self.excel, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data("data", "cfq_24_periods_test_loan.json")
		param['asset'].update(
			{
				"projectId": self.r.get("cfq_24_periods_projectId"),
				"sourceProjectId": self.r.get("cfq_24_periods_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": Common.get_repaydate(24)[0],
				"lastRepaymentDate": Common.get_repaydate(24)[-1],
				"loanTime": Common.get_time("-")
			}
		)

		for i in range(0, 96):
			period = param['repaymentPlanList'][i]['period']
			param['repaymentPlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": Common.get_repaydate(period=period)[period - 1]
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
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	# @unittest.skip("-")
	# @unittest.skipUnless(sys.argv == 'repayment', "条件成立时执行")
	def test_104_repayment(self):
		"""橙分期24期还款一期"""
		global period, plan_pay_type, plan_list_detail
		data = excel_table_byname(self.excel, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": self.r.get("cfq_24_periods_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2",
			"Fee": "3"
		}
		for i in range(0, len(param['repaymentDetailList'])):
			plan_pay_type = plan_type[param['repaymentDetailList'][i]['repaymentPlanType']]
			plan_catecory = param['repaymentDetailList'][i]['planCategory']
			asset_plan_owner = param['repaymentDetailList'][i]['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env, period=period,
						repayment_plan_type=plan_pay_type
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(repayment_detail.get('plan_pay_date')),
							"thisPayAmount": float(repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				else:
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env,
						period=period,
						repayment_plan_type="1"
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(repayment_detail.get('plan_pay_date')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			elif asset_plan_owner == "financePartner":
				if plan_catecory == 1 or plan_catecory == 2:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(user_repayment_detail.get('plan_pay_date')),
							"thisPayAmount": float(user_repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				else:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env,
						period=period,
						repayment_plan_type="1"
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(user_repayment_detail.get('plan_pay_date')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
		for i in range(0, len(param['repaymentPlanList'])):
			plan_list_pay_type = plan_type[param['repaymentPlanList'][i]['repaymentPlanType']]
			plan_list_asset_plan_owner = param['repaymentPlanList'][i]['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_24_periods_projectId"),
					environment=self.env,
					period=period,
					repayment_plan_type=plan_list_pay_type
				)
				param['repaymentPlanList'][i].update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail.get("rest_amount")),
						"payAmount": float(plan_list_detail.get("rest_amount")),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("cfq_24_periods_projectId"),
					environment=self.env,
					period=param['repaymentPlanList'][i]['period'],
					repayment_plan_type=plan_list_pay_type
				)
				param['repaymentPlanList'][i].update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail.get("rest_amount")),
						"payAmount": float(plan_list_detail.get("rest_amount")),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in range(0, len(param['feePlanList'])):
			plan_list_detail = GetSqlData.get_user_repayment_detail(
				project_id=self.r.get("cfq_24_periods_projectId"),
				environment=self.env,
				period=param['feePlanList'][i]['period'],
				repayment_plan_type="1",
				feecategory=1
			)
			param['feePlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": str(plan_list_detail.get("plan_pay_date")),
					"payTime": Common.get_time("-")
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
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])
		self.assertEqual(rep['content']['message'], "交易成功")

	# @unittest.skipUnless(sys.argv[4] == "advance_phase_one", "条件成立时执行")
	@unittest.skip("-")
	def test_105_settle_in_advance_phase_one(self):
		"""橙分期在第一期提前结清"""
		global period
		data = excel_table_byname(self.excel, 'settle_in_advance')
		print("接口名称:%s" % data[0]['casename'])
		param = Common().get_json_data('data', 'cfq_24_periods_settle_in_advance_phase_one.json')
		period = GetSqlData.get_current_period(self.r.get("cfq_24_periods_projectId"), self.env)
		# 剩余在贷本金
		debt_amount = float(GetSqlData.get_debt_amount(self.r.get("cfq_24_periods_projectId"), self.env))
		# 当期利息
		rest_interest = float(GetSqlData.get_user_repayment_detail(
			project_id=self.r.get("cfq_24_periods_projectId"),
			environment=self.env,
			period=period,
			repayment_plan_type="2").get("rest_amount"))
		param['repayment'].update(
			{
				"projectId": self.r.get("cfq_24_periods_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
				"successAmount": debt_amount + rest_interest
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2"
		}
		for i in param['repaymentDetailList']:
			i.update(
				{
					"sourceRepaymentDetailId": Common.get_random("transactionId"),
					"relatedPlanId": Common.get_random("sourceProjectId"),
					"payTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-"),
					"period": period
				}
			)
			if i['repaymentPlanType'] == 'Principal':
				i.update(
					{
						"thisPayAmount": float(GetSqlData.get_all_repayment_amount(
							environment=self.env,
							project_id=self.r.get("cfq_24_periods_projectId")
						))
					}
				)
		for i in param['repaymentPlanList']:
			i.update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"payTime": "1970-01-01 00:00:00",
					"sourceCreateTime": Common.get_time("-"),
				}
			)
			if i['repaymentStatus'] == 'repayment_done':
				if i['repaymentPlanType'] == 'Principal':
					i.update(
						{
							"curAmount": debt_amount,
							"payAmount": debt_amount,
							"planPayDate": Common.get_time("-"),
							"payTime": Common.get_time("-")
						}
					)
				elif i['repaymentPlanType'] == 'Interest':
					i.update(
						{
							"curAmount": rest_interest,
							"payAmount": rest_interest,
							"planPayDate": Common.get_time("-"),
							"payTime": Common.get_time("-")
						}
					)
			else:
				if i['assetPlanOwner'] == 'financePartner':
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env, period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']]
					)
					i.update(
						{
							"sourcePlanId": plan_list_detail.get('source_plan_id'),
							"planPayDate": str(plan_list_detail.get("plan_pay_date")),
							"curAmount": float(plan_list_detail.get("rest_amount")),
							"payAmount": float(plan_list_detail.get("rest_amount")),
						}
					)
				elif i['assetPlanOwner'] == 'foundPartner':
					plan_list_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env,
						period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']]
					)
					i.update(
						{
							"sourcePlanId": plan_list_detail.get('source_plan_id'),
							"planPayDate": str(plan_list_detail.get("plan_pay_date")),
							"curAmount": float(plan_list_detail.get("rest_amount")),
							"payAmount": float(plan_list_detail.get("rest_amount")),
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
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])
		self.assertEqual(rep['content']['message'], "交易成功")
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	@unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] == "advance_phase_two", "条件成立时执行")
	def test_105_settle_in_advance_phase_two(self):
		"""橙分期在第二期提前结清"""
		global period, plan_list_detail
		data = excel_table_byname(self.excel, 'settle_in_advance')
		print("接口名称:%s" % data[0]['casename'])
		param = Common().get_json_data('data', 'cfq_24_periods_settle_in_advance_phase_two.json')
		period = GetSqlData.get_current_period(self.r.get("cfq_24_periods_projectId"), self.env)
		# 剩余在贷本金
		debt_amount = float(GetSqlData.get_debt_amount(self.r.get("cfq_24_periods_projectId"), self.env))
		# 当期利息
		rest_interest = float(GetSqlData.get_user_repayment_detail(
			project_id=self.r.get("cfq_24_periods_projectId"),
			environment=self.env,
			period=period,
			repayment_plan_type="2"
		).get("rest_amount"))
		param['repayment'].update(
			{
				"projectId": self.r.get("cfq_24_periods_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
				"successAmount": debt_amount + rest_interest + 2875.00
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2"
		}
		for i in param['repaymentDetailList']:
			i.update(
				{
					"sourceRepaymentDetailId": Common.get_random("transactionId"),
					"relatedPlanId": Common.get_random("sourceProjectId"),
					"payTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-"),
					"period": period
				}
			)
			if i['repaymentPlanType'] == 'Principal':
				i.update(
					{
						"thisPayAmount": debt_amount
					}
				)
		for i in param['repaymentPlanList']:
			i.update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"payTime": "1970-01-01 00:00:00",
					"sourceCreateTime": Common.get_time("-"),

				}
			)
			if i['repaymentStatus'] == 'repayment_done':
				if i['repaymentPlanType'] == 'Principal':
					i.update(
						{
							"curAmount": debt_amount,
							"payAmount": debt_amount,
							"planPayDate": Common.get_time("-"),
							"payTime": Common.get_time("-")
						}
					)
				elif i['repaymentPlanType'] == 'Interest':
					i.update(
						{
							"curAmount": rest_interest,
							"payAmount": rest_interest,
							"planPayDate": Common.get_time("-"),
							"payTime": Common.get_time("-")
						}
					)
			else:
				if i['assetPlanOwner'] == 'financePartner':
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env,
						period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']]
					)
					i.update(
						{
							"sourcePlanId": plan_list_detail.get('source_plan_id'),
							"planPayDate": str(plan_list_detail.get("plan_pay_date")),
							"curAmount": float(plan_list_detail.get("rest_amount")),
							"payAmount": float(plan_list_detail.get("rest_amount")),
						}
					)
				elif i['assetPlanOwner'] == 'foundPartner':
					plan_list_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env,
						period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']]
					)
					i.update(
						{
							"sourcePlanId": plan_list_detail.get('source_plan_id'),
							"planPayDate": str(plan_list_detail.get("plan_pay_date")),
							"curAmount": float(plan_list_detail.get("rest_amount")),
							"payAmount": float(plan_list_detail.get("rest_amount")),
						}
					)
		for i in param['feePlanList']:
			i.update(
				{
					"sourceRepaymentDetailId": Common.get_random("transactionId"),
					"relatedPlanId": Common.get_random("sourceProjectId"),
					"payTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-"),
					"period": period,
					"planPayDate": Common.get_time("-")
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
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])
		self.assertEqual(rep['content']['message'], "交易成功")
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	@unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] == "compensation", "条件成立时执行")
	def test_106_compensation(self):
		"""橙分期24期代偿一期"""
		data = excel_table_byname(self.excel, 'compensation')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": self.r.get("cfq_24_periods_projectId"),
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": self.r.get("cfq_24_periods_projectId"),
					"sourceDetailId": Common.get_random("serviceSn"),
					"sourceSwapId": Common.get_random("serviceSn"),
					"sourceRelatedPlanId": Common.get_random("serviceSn"),
					"actionTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-")
				}
			)
		for i in param['repaymentPlanList']:
			global plan_list_detail, plan_pay_type
			plan_pay_type = {
				"Principal": "1",
				"Interest": "2"
			}
			if i['assetPlanOwner'] == "foundPartner":
				plan_list_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("cfq_24_periods_projectId"),
					environment=self.env,
					period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType'])
				)
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_24_periods_projectId"),
					environment=self.env,
					period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType'])
				)
			i.update(
				{
					"sourcePlanId": plan_list_detail.get("source_plan_id"),
					"planPayDate": str(plan_list_detail.get("plan_pay_date"))
				}
			)
		for i in param['feePlanList']:
			i.update(
				{
					"sourcePlanId": Common.get_random("serviceSn"),
					"planPayDate": Common.get_time("-"),
					"sourceRepaymentDetailId": Common.get_random("serviceSn"),
					"relatedPlanId": Common.get_random("serviceSn"),
					"sourceCreateTime": Common.get_time("-")
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
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])

	@unittest.skip("-")
	def test_107_repurchase(self):
		"""橙分期24期回购一期"""
		data = excel_table_byname(self.excel, 'repurchase')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": self.r.get("cfq_24_periods_projectId"),
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": self.r.get("cfq_24_periods_projectId"),
					"sourceDetailId": Common.get_random("serviceSn"),
					"sourceSwapId": Common.get_random("serviceSn"),
					"sourceRelatedPlanId": Common.get_random("serviceSn"),
					"actionTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-")
				}
			)
		for i in param['repaymentPlanList']:
			global plan_list_detail, plan_pay_type
			plan_pay_type = {
				"Principal": "1",
				"Interest": "2"
			}
			if i['assetPlanOwner'] == "foundPartner":
				plan_list_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("cfq_24_periods_projectId"),
					environment=self.env,
					period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType'])
				)
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_24_periods_projectId"),
					environment=self.env,
					period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType'])
				)
			i.update(
				{
					"sourcePlanId": plan_list_detail.get("source_plan_id"),
					"planPayDate": plan_list_detail.get("plan_pay_date")
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
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])

	@unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] == "compensation_after_repay", "条件成立时执行")
	def test_108_after_comp_repay(self):
		"""橙分期24期代偿后还款"""
		global period, plan_pay_type, plan_list_detail
		data = excel_table_byname(self.excel, 'after_comp_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": self.r.get("cfq_24_periods_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2",
			"Fee": "3"
		}
		fee_id = Common.get_random("serviceSn")
		for i in range(0, len(param['repaymentDetailList'])):
			plan_pay_type = plan_type[param['repaymentDetailList'][i]['repaymentPlanType']]
			plan_catecory = param['repaymentDetailList'][i]['planCategory']
			asset_plan_owner = param['repaymentDetailList'][i]['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"relatedPlanId": repayment_detail.get("source_plan_id"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(repayment_detail.get('plan_pay_date')),
							"thisPayAmount": float(repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				else:
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env,
						period=period,
						repayment_plan_type='1',
						feecategory=1
						# feecategory=param['repaymentDetailList'][i]['planCategory']
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"relatedPlanId": fee_id,
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(plan_list_detail.get("plan_pay_date")),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			elif asset_plan_owner == "financePartner":
				if plan_catecory == 1 or plan_catecory == 2:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("cfq_24_periods_projectId"),
						environment=self.env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"relatedPlanId": user_repayment_detail.get("source_plan_id"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(user_repayment_detail.get('plan_pay_date')),
							"thisPayAmount": float(user_repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			else:
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_24_periods_projectId"),
					environment=self.env,
					period=period,
					repayment_plan_type='1',
					feecategory=1
				)
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": Common.get_time("-"),
						"planPayDate": str(plan_list_detail.get("plan_pay_date")),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in range(0, len(param['repaymentPlanList'])):
			plan_list_pay_type = plan_type[param['repaymentPlanList'][i]['repaymentPlanType']]
			plan_list_asset_plan_owner = param['repaymentPlanList'][i]['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_24_periods_projectId"),
					environment=self.env,
					period=period,
					repayment_plan_type=plan_list_pay_type
				)
				param['repaymentPlanList'][i].update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail.get('cur_amount')),
						"payAmount": float(plan_list_detail.get('rest_amount')),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("cfq_24_periods_projectId"),
					environment=self.env,
					period=param['repaymentPlanList'][i]['period'],
					repayment_plan_type=plan_list_pay_type
				)
				param['repaymentPlanList'][i].update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail.get('cur_amount')),
						"payAmount": float(plan_list_detail.get('rest_amount')),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in range(0, len(param['feePlanList'])):
			if param['feePlanList'][i]['assetPlanOwner'] == 'foundPartner':
				param['feePlanList'][i].update(
					{
						"sourcePlanId": fee_id,
						"planPayDate": Common.get_time("-"),
						"payTime": Common.get_time("-")
					}
				)
			else:
				param['feePlanList'][i].update(
					{
						"sourcePlanId": Common.get_random('userid'),
						"planPayDate": Common.get_time("-"),
						"payTime": Common.get_time("-")
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
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])
		self.assertEqual(rep['content']['message'], "交易成功")


if __name__ == '__main__':
	unittest.main()
