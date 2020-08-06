#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth: buxiangjie
@date:
@describe: 橙分期12期
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

logger = Logger(logger="test_cfq_12_periods_tp").getlog()


class Cfq12PeriodsTp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = 'qa'
		cls.sql = GetSqlData()
		cls.r = Common.conn_redis(enviroment=cls.env)
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_approved(self):
		"""橙分期进件同意接口"""
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		Common.p2p_get_userinfo("cfq_12_periods", self.env)
		self.r.mset(
			{
				"cfq_12_periods_sourceProjectId": Common.get_random("sourceProjectId"),
				"cfq_12_periods_sourceUserId": Common.get_random("userid"),
				"cfq_12_periods_transactionId": "Apollo" + Common.get_random("transactionId"),
				"cfq_12_periods_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("cfq_12_periods_sourceProjectId"),
				"sourceUserId": self.r.get("cfq_12_periods_sourceUserId"),
				"transactionId": self.r.get("cfq_12_periods_transactionId")
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time("-"),
				"applyTerm": 12,
				"applyAmount": 500.00
			}
		)
		param['personalInfo'].update(
			{
				# "cardNum": self.r.get()("cfq_12_periods_cardNum"),
				# "custName": self.r.get()("cfq_12_periods_custName"),
				# "phone": self.r.get()("cfq_12_periods_phone")
				# "cardNum": "321323196308030008",
				# "custName": "王军",
				# "phone": "19972598351"
				"cardNum": "412727199202164546",
				"custName": "李杰",
				"phone": "18300696035"
			}
		)
		param['loanInfo'].update(
			{
				"loanAmount": 500.00,
				"loanTerm": 12,
			}
		)
		param['cardInfo'].update({"bankPhone": self.r.get("cfq_12_periods_phone")})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.r.set("cfq_12_periods_projectId", json.loads(rep.text)['content']['projectId'])
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))
		# 修改进件审核状态
		GetSqlData.change_project_audit_status(
			project_id=self.r.get("cfq_12_periods_projectId"),
			enviroment=self.env
		)

	def test_101_query_audit_status(self):
		"""橙分期进件审核结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=self.r.get("cfq_12_periods_projectId"),
			enviroment=self.env
		)
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'query_audit_status')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("cfq_12_periods_sourceProjectId"),
				"projectId": self.r.get("cfq_12_periods_projectId")
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("返回信息:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))

	def test_101_loan_notice(self):
		"""橙分期放款通知接口"""
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("cfq_12_periods_sourceProjectId"),
				"sourceUserId": self.r.get("cfq_12_periods_sourceUserId"),
				"projectId": self.r.get("cfq_12_periods_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("cfq_12_periods_cardNum"),
				"bankPhone": self.r.get("cfq_12_periods_phone"),
				"loanTime": Common.get_time("-")
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("返回信息:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))

	def test_102_loanasset(self):
		"""橙分期进件放款同步接口"""
		global period
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		first_year = str(Common.get_repaydate(12)[0].split(' ')[0].split('-')[0])
		first_day = str(Common.get_repaydate(12)[0].split(' ')[0].split('-')[1])
		last_year = str(Common.get_repaydate(12)[-1].split(' ')[0].split('-')[0])
		last_day = str(Common.get_repaydate(12)[-1].split(' ')[0].split('-')[1])
		param['asset'].update(
			{
				"projectId": self.r.get("cfq_12_periods_projectId"),
				"sourceProjectId": self.r.get("cfq_12_periods_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				# "firstRepaymentDate": first_year + '-' + first_day + '-' + '10 23:59:59',
				"firstRepaymentDate": '2020-07-10 23:59:59',
				"lastRepaymentDate": last_year + '-' + last_day + '-' + '10 23:59:59',
				"loanTime": Common.get_time("-")
			}
		)

		for i in range(0, 48):
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))

	# @unittest.skip("-")
	def test_103_sign_borrow(self):
		"""上传借款协议"""
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'cfq_sign_borrow.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": self.r.get('cfq_12_periods_sourceUserId'),
				"contractType": 2,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": self.r.get('cfq_12_periods_transactionId'),
				"associationId": self.r.get('cfq_12_periods_projectId')
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
			product="pintic",
			enviroment=self.env
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.r.set("cfq_12_periods_contractId", json.loads(rep.text)['content']['contractId'])
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['resultCode']))

	@unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] == "repayment", "条件成立时执行")
	def test_104_repayment(self):
		"""橙分期12期还款一期"""
		global period, plan_pay_type, plan_list_detail
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": self.r.get("cfq_12_periods_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
				"successAmount": float(GetSqlData.get_user_repayment_amount(
					enviroment=self.env,
					project_id=self.r.get("cfq_12_periods_projectId"),
					period=period)
				)
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2",
			"Fee": "3"
		}
		repaydate = Common.get_repaydate(12)
		for i in range(0, len(param['repaymentDetailList'])):
			plan_pay_type = plan_type[param['repaymentDetailList'][i]['repaymentPlanType']]
			plan_catecory = param['repaymentDetailList'][i]['planCategory']
			asset_plan_owner = param['repaymentDetailList'][i]['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("cfq_12_periods_projectId"),
						enviroment=self.env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": repayment_detail.get('plan_pay_date'),
							"thisPayAmount": float(repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				else:
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("cfq_12_periods_projectId"),
						enviroment=self.env,
						period=period,
						repayment_plan_type=3,
						feecategory=param['repaymentDetailList'][i]['planCategory']
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": repaydate[0].split(" ")[0],
							"thisPayAmount": float(plan_list_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			elif asset_plan_owner == "financePartner":
				user_repayment_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_12_periods_projectId"),
					enviroment=self.env,
					period=period,
					repayment_plan_type=plan_pay_type
				)
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": Common.get_time("-"),
						"planPayDate": user_repayment_detail.get('plan_pay_date'),
						"thisPayAmount": float(user_repayment_detail.get('rest_amount')),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
			else:
				pass
		for i in range(0, len(param['repaymentPlanList'])):
			plan_list_pay_type = plan_type[param['repaymentPlanList'][i]['repaymentPlanType']]
			plan_list_asset_plan_owner = param['repaymentPlanList'][i]['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_12_periods_projectId"),
					enviroment=self.env,
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
					project_id=self.r.get("cfq_12_periods_projectId"),
					enviroment=self.env,
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
		param['feePlanList'] = []
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])
		self.assertEqual(json.loads(rep.text)['content']['message'], "交易成功")

	# @unittest.skipUnless(sys.argv[4] == "advance_phase_one", "条件成立时执行")
	@unittest.skip("-")
	def test_105_settle_in_advance_phase_one(self):
		"""橙分期在第一期提前结清"""
		global period
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'settle_in_advance')
		print("接口名称:%s" % data[0]['casename'])
		param = Common().get_json_data('data', 'cfq_12_periods_settle_in_advance_phase_one.json')
		period = GetSqlData.get_current_period(self.r.get("cfq_12_periods_projectId"), self.env)
		# 剩余在贷本金
		debt_amount = float(GetSqlData.get_debt_amount(self.r.get("cfq_12_periods_projectId"), self.env))
		# 当期利息
		rest_interest = float(GetSqlData.get_user_repayment_detail(
			project_id=self.r.get("cfq_12_periods_projectId"), enviroment=self.env, period=period,
			repayment_plan_type="2"
		).get("rest_amount"))
		param['repayment'].update(
			{
				"projectId": self.r.get("cfq_12_periods_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2",
			"Fee": '3'
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
						"thisPayAmount": GetSqlData.get_all_repayment_amount(
							enviroment=self.env,
							project_id=self.r.get("cfq_12_periods_projectId")
						)
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
						project_id=self.r.get("cfq_12_periods_projectId"),
						enviroment=self.env, period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']])
					i.update(
						{
							"sourcePlanId": plan_list_detail.get('source_plan_id'),
							"planPayDate": plan_list_detail.get("plan_pay_date"),
							"curAmount": float(plan_list_detail.get("rest_amount")),
							"payAmount": float(plan_list_detail.get("rest_amount")),
						}
					)
				elif i['assetPlanOwner'] == 'foundPartner':
					plan_list_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("cfq_12_periods_projectId"),
						enviroment=self.env, period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']])
					i.update(
						{
							"sourcePlanId": plan_list_detail.get('source_plan_id'),
							"planPayDate": plan_list_detail.get("plan_pay_date"),
							"curAmount": float(plan_list_detail.get("rest_amount")),
							"payAmount": float(plan_list_detail.get("rest_amount")),
						}
					)
		for i in param['feePlanList']:
			i.update(
				{
					"sourcePlanId": Common.get_random('serviceSn'),
					"planPayDate": Common.get_time('-'),
					'payTime': Common.get_time('-')
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
				enviroment=self.env,
				product="pintic"
			)
			print("响应信息:%s" % rep)
			print("返回json:%s" % rep.text)
			logger.info("返回信息:%s" % rep.text)
			self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])
			self.assertEqual(json.loads(rep.text)['content']['message'], "交易成功")
			self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))

	@unittest.skip("-")
	def test_106_settle_in_advance_phase_two(self):
		"""橙分期在第二期提前结清"""
		global period, plan_list_detail
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'settle_in_advance')
		print("接口名称:%s" % data[0]['casename'])
		param = Common().get_json_data('data', 'cfq_12_periods_settle_in_advance_phase_two.json')
		period = GetSqlData.get_current_period(self.r.get("cfq_12_periods_projectId"), self.env)
		# 剩余在贷本金
		debt_amount = float(
			GetSqlData.get_debt_amount(self.r.get("cfq_12_periods_projectId"), self.env))
		# 当期利息
		rest_interest = float(GetSqlData.get_user_repayment_detail(
			project_id=self.r.get("cfq_12_periods_projectId"), enviroment=self.env, period=period,
			repayment_plan_type="2"
		).get("rest_amount"))
		param['repayment'].update(
			{
				"projectId": self.r.get("cfq_12_periods_projectId"),
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
						project_id=self.r.get("cfq_12_periods_projectId"),
						enviroment=self.env, period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']])
					i.update(
						{
							"sourcePlanId": plan_list_detail.get('source_plan_id'),
							"planPayDate": plan_list_detail.get("plan_pay_date"),
							"curAmount": float(plan_list_detail.get("rest_amount")),
							"payAmount": float(plan_list_detail.get("rest_amount")),
						}
					)
				elif i['assetPlanOwner'] == 'foundPartner':
					plan_list_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("cfq_12_periods_projectId"),
						enviroment=self.env, period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']])
					i.update(
						{
							"sourcePlanId": plan_list_detail.get('source_plan_id'),
							"planPayDate": plan_list_detail.get("plan_pay_date"),
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])
		self.assertEqual(json.loads(rep.text)['content']['message'], "交易成功")
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))

	@unittest.skip("-")
	def test_107_compensation(self):
		"""橙分期12期代偿一期"""
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'compensation')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": self.r.get("cfq_12_periods_projectId"),
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": self.r.get("cfq_12_periods_projectId"),
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
					project_id=self.r.get("cfq_12_periods_projectId"),
					enviroment=self.env, period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType']))
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_12_periods_projectId"),
					enviroment=self.env, period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType']))
			i.update(
				{
					"sourcePlanId": plan_list_detail.get("source_plan_id"),
					"planPayDate": plan_list_detail.get("plan_pay_date")
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])

	@unittest.skip("-")
	def test_108_repurchase(self):
		"""橙分期12期回购一期"""
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'repurchase')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": self.r.get("cfq_12_periods_projectId"),
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": self.r.get("cfq_12_periods_projectId"),
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
					project_id=self.r.get("cfq_12_periods_projectId"),
					enviroment=self.env, period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType']))
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_12_periods_projectId"),
					enviroment=self.env, period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType']))
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])

	@unittest.skip("-")
	def test_109_after_comp_repay(self):
		"""橙分期12期代偿后还款"""
		global period, plan_pay_type, plan_list_detail
		excel = self.excel + Config().Get_Item('File', 'cfq_12_periods_case_file')
		data = excel_table_byname(excel, 'after_comp_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": self.r.get("cfq_12_periods_projectId"),
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
		for i in range(0, len(param['repaymentDetailList'])):
			plan_pay_type = plan_type[param['repaymentDetailList'][i]['repaymentPlanType']]
			plan_catecory = param['repaymentDetailList'][i]['planCategory']
			asset_plan_owner = param['repaymentDetailList'][i]['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("cfq_12_periods_projectId"),
						enviroment=self.env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": repayment_detail.get('plan_pay_date'),
							"thisPayAmount": repayment_detail.get('rest_amount'),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				else:
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("cfq_12_periods_projectId"),
						enviroment=self.env,
						period=period,
						repayment_plan_type=3,
						feecategory=param['repaymentDetailList'][i]['planCategory']
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": plan_list_detail.get("plan_pay_date"),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			elif asset_plan_owner == "financePartner":
				if plan_catecory == 1 or plan_catecory == 2:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("cfq_12_periods_projectId"),
						enviroment=self.env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": user_repayment_detail.get('plan_pay_date'),
							"thisPayAmount": user_repayment_detail.get('rest_amount'),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			else:
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_12_periods_projectId"),
					enviroment=self.env,
					period=period,
					repayment_plan_type=3,
					feecategory=param['repaymentDetailList'][i]['planCategory']
				)
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": Common.get_time("-"),
						"planPayDate": plan_list_detail.get("plan_pay_date"),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in range(0, len(param['repaymentPlanList'])):
			plan_list_pay_type = plan_type[param['repaymentPlanList'][i]['repaymentPlanType']]
			plan_list_asset_plan_owner = param['repaymentPlanList'][i]['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("cfq_12_periods_projectId"),
					enviroment=self.env,
					period=period,
					repayment_plan_type=plan_list_pay_type
				)
				param['repaymentPlanList'][i].update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": plan_list_detail.get('cur_amount'),
						"payAmount": plan_list_detail.get('rest_amount'),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("cfq_12_periods_projectId"),
					enviroment=self.env,
					period=param['repaymentPlanList'][i]['period'],
					repayment_plan_type=plan_list_pay_type
				)
				param['repaymentPlanList'][i].update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": plan_list_detail.get('cur_amount'),
						"payAmount": plan_list_detail.get('rest_amount'),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in range(0, len(param['feePlanList'])):
			plan_list_detail = GetSqlData.get_user_repayment_detail(
				project_id=self.r.get("cfq_12_periods_projectId"),
				enviroment=self.env,
				period=param['feePlanList'][i]['period'],
				repayment_plan_type=3,
				feecategory=param['feePlanList'][i]['feeCategory']
			)
			param['feePlanList'][i].update(
				{
					"sourcePlanId": plan_list_detail.get('source_plan_id'),
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])
		self.assertEqual(json.loads(rep.text)['content']['message'], "交易成功")


if __name__ == '__main__':
	unittest.main()
