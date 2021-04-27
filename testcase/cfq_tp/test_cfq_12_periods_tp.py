#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth: buxiangjie
@date:
@describe: 橙分期12期
"""
import os
import json
import sys
import pytest
import allure

from common.common_func import Common
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@allure.feature("橙分期12期")
@pytest.mark.skip("业务暂停")
class TestCfq12PeriodsTp:
	file = Config().get_item('File', 'cfq_12_periods_case_file')

	@allure.title("橙分期进件")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle_in_advance
	@pytest.mark.comp
	@pytest.mark.comp_repay
	@pytest.mark.repay_two_periods
	def test_100_approved(self, r, env):
		"""橙分期进件同意接口"""
		data = excel_table_byname(self.file, 'approved')
		param = json.loads(data[0]['param'])
		Common.p2p_get_userinfo("cfq_12_periods", env)
		r.mset(
			{
				"cfq_12_periods_sourceProjectId": Common.get_random("sourceProjectId"),
				"cfq_12_periods_sourceUserId": Common.get_random("userid"),
				"cfq_12_periods_transactionId": "Apollo" + Common.get_random("transactionId"),
				"cfq_12_periods_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": r.get("cfq_12_periods_sourceProjectId"),
				"sourceUserId": r.get("cfq_12_periods_sourceUserId"),
				"transactionId": r.get("cfq_12_periods_transactionId")
			}
		)
		# param['applyInfo'].update(
		# 	{
		# 		"applyTime": Common.get_time("-"),
		# 		"applyTerm": 12,
		# 		"applyAmount": 500.00
		# 	}
		# )
		param['personalInfo'].update(
			{
				"cardNum": r.get("cfq_12_periods_cardNum"),
				"custName": r.get("cfq_12_periods_custName"),
				"phone": r.get("cfq_12_periods_phone")
			}
		)
		# param['loanInfo'].update(
		# 	{
		# 		"loanAmount": 500.00,
		# 		"loanTerm": 12,
		# 	}
		# )
		param['cardInfo'].update({"bankPhone": r.get("cfq_12_periods_phone")})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			environment=env,
			product="pintec"
		)
		r.set("cfq_12_periods_projectId", rep['content']['projectId'])
		assert rep['resultCode'], int(data[0]['msgCode'])

	@allure.title("橙分期进件审核结果查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.comp
	@pytest.mark.comp_repay
	@pytest.mark.repay_two_periods
	def test_101_query_audit_status(self, r, env):
		"""橙分期进件审核结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=r.get("cfq_12_periods_projectId"),
			environment=env
		)
		data = excel_table_byname(self.file, 'query_audit_status')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get("cfq_12_periods_sourceProjectId"),
				"projectId": r.get("cfq_12_periods_projectId")
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
			environment=env,
			product="pintec"
		)
		assert rep['resultCode'], int(data[0]['msgCode'])

	@allure.title("橙分期放款通知")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.comp
	@pytest.mark.comp_repay
	@pytest.mark.repay_two_periods
	def test_101_loan_notice(self, r, env):
		"""橙分期放款通知接口"""
		data = excel_table_byname(self.file, 'loan_notice')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get("cfq_12_periods_sourceProjectId"),
				"sourceUserId": r.get("cfq_12_periods_sourceUserId"),
				"projectId": r.get("cfq_12_periods_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": r.get("cfq_12_periods_cardNum"),
				"bankPhone": r.get("cfq_12_periods_phone"),
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
			environment=env,
			product="pintec"
		)
		assert rep['resultCode'], int(data[0]['msgCode'])

	@allure.title("橙分期放款同步")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.comp
	@pytest.mark.comp_repay
	@pytest.mark.repay_two_periods
	def test_102_loanasset(self, r, env):
		"""橙分期进件放款同步接口"""
		data = excel_table_byname(self.file, 'loan_asset')
		param = json.loads(data[0]['param'])
		first_year = str(Common.get_repaydate(12)[0].split(' ')[0].split('-')[0])
		first_day = str(Common.get_repaydate(12)[0].split(' ')[0].split('-')[1])
		last_year = str(Common.get_repaydate(12)[-1].split(' ')[0].split('-')[0])
		last_day = str(Common.get_repaydate(12)[-1].split(' ')[0].split('-')[1])
		param['asset'].update(
			{
				"projectId": r.get("cfq_12_periods_projectId"),
				"sourceProjectId": r.get("cfq_12_periods_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": first_year + '-' + first_day + '-' + '10 23:59:59',
				# "firstRepaymentDate": '2020-07-10 23:59:59',
				"lastRepaymentDate": last_year + '-' + last_day + '-' + '10 23:59:59',
				"loanTime": Common.get_time("-")
			}
		)

		for i in param['repaymentPlanList']:
			period = i['period']
			i.update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": "-".join(
						Common.get_repaydate(period=period)[period - 1].split(" ")[0].split("-")[0:2]) + "-10"
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
			environment=env,
			product="pintec"
		)
		assert rep['resultCode'], int(data[0]['msgCode'])

	@allure.title("橙分期上传借款协议")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.comp
	@pytest.mark.comp_repay
	@pytest.mark.repay_two_periods
	def test_103_sign_borrow(self, r, env):
		"""上传借款协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'cfq_sign_borrow.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('cfq_12_periods_sourceUserId'),
				"contractType": 2,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get('cfq_12_periods_transactionId'),
				"associationId": r.get('cfq_12_periods_projectId')
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
			product="pintec",
			environment=env
		)
		r.set("cfq_12_periods_contractId", rep['content']['contractId'])
		assert rep['resultCode'], int(data[0]['resultCode'])

	@allure.title("橙分期还款一期")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_104_repayment(self, r, env):
		"""橙分期12期还款一期"""
		data = excel_table_byname(self.file, 'repayment')
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": r.get("cfq_12_periods_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
				"successAmount": float(GetSqlData.get_user_repayment_amount(
					environment=env,
					project_id=r.get("cfq_12_periods_projectId"),
					period=period)
				)
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2",
			"Fee": "3"
		}
		for i in param['repaymentDetailList']:
			plan_pay_type = plan_type[i['repaymentPlanType']]
			plan_catecory = i['planCategory']
			asset_plan_owner = i['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail = GetSqlData.get_repayment_plan_date(project_id=r.get("cfq_12_periods_projectId"),
																		  environment=env,
																		  repayment_plan_type=plan_pay_type,
																		  period=period)
					i.update(
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
					plan_list_detail2 = GetSqlData.get_user_repayment_detail(
						project_id=r.get("cfq_12_periods_projectId"),
						environment=env,
						period=period,
						repayment_plan_type=3,
						feecategory=i['planCategory']
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(plan_list_detail2.get("plan_pay_date")),
							"thisPayAmount": float(plan_list_detail2.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			elif asset_plan_owner == "financePartner":
				user_repayment_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("cfq_12_periods_projectId"),
					environment=env,
					period=period,
					repayment_plan_type=plan_pay_type
				)
				i.update(
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
				pass
		for i in param['repaymentPlanList']:
			plan_list_pay_type = plan_type[i['repaymentPlanType']]
			plan_list_asset_plan_owner = i['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("cfq_12_periods_projectId"),
					environment=env,
					period=period,
					repayment_plan_type=plan_list_pay_type
				)
				i.update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": str(plan_list_detail.get("plan_pay_date")),
						"curAmount": float(plan_list_detail.get("rest_amount")),
						"payAmount": float(plan_list_detail.get("rest_amount")),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail2 = GetSqlData.get_repayment_plan_date(project_id=r.get("cfq_12_periods_projectId"),
																	   environment=env,
																	   repayment_plan_type=plan_list_pay_type,
																	   period=i['period'])
				i.update(
					{
						"sourcePlanId": plan_list_detail2.get('source_plan_id'),
						"planPayDate": str(plan_list_detail2.get("plan_pay_date")),
						"curAmount": float(plan_list_detail2.get("rest_amount")),
						"payAmount": float(plan_list_detail2.get("rest_amount")),
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
			data=json.dumps(param, ensure_ascii=False),
			environment=env,
			product="pintec"
		)
		assert rep['resultCode'] == data[0]['msgCode']
		assert rep['content']['message'] == "交易成功"

	@allure.title("橙分期第一期提前结清")
	@allure.severity("blocker")
	@pytest.mark.settle_in_advance
	def test_105_settle_in_advance_phase_one(self, r, env):
		"""橙分期在第一期提前结清"""
		data = excel_table_byname(self.file, 'settle_in_advance')
		param = Common().get_json_data('data', 'cfq_12_periods_settle_in_advance_phase_one.json')
		period = GetSqlData.get_current_period(r.get("cfq_12_periods_projectId"), env)
		# 剩余在贷本金
		debt_amount = float(GetSqlData.get_debt_amount(r.get("cfq_12_periods_projectId"), env))
		# 当期利息
		rest_interest = float(GetSqlData.get_user_repayment_detail(
			project_id=r.get("cfq_12_periods_projectId"), environment=env, period=period,
			repayment_plan_type="2"
		).get("rest_amount"))
		param['repayment'].update(
			{
				"projectId": r.get("cfq_12_periods_projectId"),
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
							environment=env,
							project_id=r.get("cfq_12_periods_projectId")
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
					plan_list_detail1 = GetSqlData.get_user_repayment_detail(
						project_id=r.get("cfq_12_periods_projectId"),
						environment=env, period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']])
					i.update(
						{
							"sourcePlanId": plan_list_detail1.get('source_plan_id'),
							"planPayDate": str(plan_list_detail1.get("plan_pay_date")),
							"curAmount": float(plan_list_detail1.get("rest_amount")),
							"payAmount": float(plan_list_detail1.get("rest_amount")),
						}
					)
				elif i['assetPlanOwner'] == 'foundPartner':
					plan_list_detail2 = GetSqlData.get_repayment_plan_date(project_id=r.get("cfq_12_periods_projectId"),
																		   environment=env,
																		   repayment_plan_type=plan_type[
																			   i['repaymentPlanType']],
																		   period=i['period'])
					i.update(
						{
							"sourcePlanId": plan_list_detail2.get('source_plan_id'),
							"planPayDate": str(plan_list_detail2.get("plan_pay_date")),
							"curAmount": float(plan_list_detail2.get("rest_amount")),
							"payAmount": float(plan_list_detail2.get("rest_amount")),
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
				data=json.dumps(param, ensure_ascii=False),
				environment=env,
				product="pintec"
			)

			assert rep['resultCode'] == data[0]['msgCode']
			assert rep['content']['message'] == "交易成功"
			assert rep['resultCode'], int(data[0]['msgCode'])

	@allure.title("橙分期代偿一期")
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_107_compensation(self, r, env):
		"""橙分期12期代偿一期"""
		data = excel_table_byname(self.file, 'compensation')
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": r.get("cfq_12_periods_projectId"),
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": r.get("cfq_12_periods_projectId"),
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
				plan_list_detail = GetSqlData.get_repayment_plan_date(project_id=r.get("cfq_12_periods_projectId"),
																	  environment=env,
																	  repayment_plan_type=plan_pay_type.get(
																		  i['repaymentPlanType']), period=i['period'])
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("cfq_12_periods_projectId"),
					environment=env, period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType']))
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
			environment=env,
			product="pintec"
		)
		assert rep['resultCode'] == data[0]['msgCode']

	def test_108_repurchase(self, r, env):
		"""橙分期12期回购一期"""
		data = excel_table_byname(self.file, 'repurchase')
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": r.get("cfq_12_periods_projectId"),
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": r.get("cfq_12_periods_projectId"),
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
				plan_list_detail = GetSqlData.get_repayment_plan_date(project_id=r.get("cfq_12_periods_projectId"),
																	  environment=env,
																	  repayment_plan_type=plan_pay_type.get(
																		  i['repaymentPlanType']), period=i['period'])
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("cfq_12_periods_projectId"),
					environment=env, period=i['period'],
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
			data=json.dumps(param, ensure_ascii=False),
			environment=env,
			product="pintec"
		)
		assert rep['resultCode'] == data[0]['msgCode']

	@allure.title("橙分期代偿后还款")
	@pytest.mark.comp_repay
	def test_109_after_comp_repay(self, r, env):
		"""橙分期12期代偿后还款"""
		data = excel_table_byname(self.file, 'after_comp_repay')
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": r.get("cfq_12_periods_projectId"),
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
		for i in param['repaymentDetailList']:
			plan_pay_type = plan_type[i['repaymentPlanType']]
			plan_catecory = i['planCategory']
			asset_plan_owner = i['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail1 = GetSqlData.get_repayment_plan_date(project_id=r.get("cfq_12_periods_projectId"),
																		   environment=env,
																		   repayment_plan_type=plan_pay_type,
																		   period=period)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(repayment_detail1.get('plan_pay_date')),
							"thisPayAmount": float(repayment_detail1.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				else:
					plan_list_detail2 = GetSqlData.get_user_repayment_detail(
						project_id=r.get("cfq_12_periods_projectId"),
						environment=env,
						period=period,
						repayment_plan_type=3,
						feecategory=i['planCategory']
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(plan_list_detail2.get("plan_pay_date")),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			elif asset_plan_owner == "financePartner":
				if plan_catecory == 1 or plan_catecory == 2:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=r.get("cfq_12_periods_projectId"),
						environment=env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					i.update(
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
				plan_list_detail3 = GetSqlData.get_user_repayment_detail(
					project_id=r.get("cfq_12_periods_projectId"),
					environment=env,
					period=period,
					repayment_plan_type=3,
					feecategory=i['planCategory']
				)
				i.update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": Common.get_time("-"),
						"planPayDate": str(plan_list_detail3.get("plan_pay_date")),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in param['repaymentPlanList']:
			plan_list_pay_type = plan_type[i['repaymentPlanType']]
			plan_list_asset_plan_owner = i['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail4 = GetSqlData.get_user_repayment_detail(
					project_id=r.get("cfq_12_periods_projectId"),
					environment=env,
					period=period,
					repayment_plan_type=plan_list_pay_type
				)
				i.update(
					{
						"sourcePlanId": plan_list_detail4.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail4.get('cur_amount')),
						"payAmount": float(plan_list_detail4.get('rest_amount')),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail5 = GetSqlData.get_repayment_plan_date(project_id=r.get("cfq_12_periods_projectId"),
																	   environment=env,
																	   repayment_plan_type=plan_list_pay_type,
																	   period=i['period'])
				i.update(
					{
						"sourcePlanId": plan_list_detail5.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail5.get('cur_amount')),
						"payAmount": float(plan_list_detail5.get('rest_amount')),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in param['feePlanList']:
			plan_list_detail6 = GetSqlData.get_user_repayment_detail(
				project_id=r.get("cfq_12_periods_projectId"),
				environment=env,
				period=i['period'],
				repayment_plan_type=3,
				feecategory=i['feeCategory']
			)
			i.update(
				{
					"sourcePlanId": plan_list_detail6.get('source_plan_id'),
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
			environment=env,
			product="pintec"
		)
		assert rep['resultCode'] == data[0]['msgCode']
		assert rep['content']['message'] == "交易成功"

	@allure.title("橙分期一次还款2期")
	@pytest.mark.repay_two_periods
	def test_repay_two_periods(self, r, env):
		"""橙分期一次还款2期"""
		data = excel_table_byname(self.file, 'repay_two_periods')
		param = json.loads(data[0]['param'])
		param['repayment'].update(
			{
				"projectId": r.get("cfq_12_periods_projectId"),
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
		for i in param['repaymentDetailList']:
			plan_pay_type = plan_type[i['repaymentPlanType']]
			plan_catecory = i['planCategory']
			asset_plan_owner = i['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail1 = GetSqlData.get_repayment_plan_date(project_id=r.get("cfq_12_periods_projectId"),
																		   environment=env,
																		   repayment_plan_type=plan_pay_type,
																		   period=i['period'])
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(repayment_detail1.get('plan_pay_date')),
							"thisPayAmount": float(repayment_detail1.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": i['period']
						}
					)
				else:
					plan_list_detail2 = GetSqlData.get_user_repayment_detail(
						project_id=r.get("cfq_12_periods_projectId"),
						environment=env,
						period=i['period'],
						repayment_plan_type=3,
						feecategory=i['planCategory']
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(plan_list_detail2.get("plan_pay_date")),
							"payTime": Common.get_time("-"),
							"period": i['period']
						}
					)
			elif asset_plan_owner == "financePartner":
				if plan_catecory == 1 or plan_catecory == 2:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=r.get("cfq_12_periods_projectId"),
						environment=env,
						period=i['period'],
						repayment_plan_type=plan_pay_type
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(user_repayment_detail.get('plan_pay_date')),
							"thisPayAmount": float(user_repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": i['period']
						}
					)
			else:
				plan_list_detail3 = GetSqlData.get_user_repayment_detail(
					project_id=r.get("cfq_12_periods_projectId"),
					environment=env,
					period=i['period'],
					repayment_plan_type=3,
					feecategory=i['planCategory']
				)
				i.update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": Common.get_time("-"),
						"planPayDate": str(plan_list_detail3.get("plan_pay_date")),
						"payTime": Common.get_time("-"),
						"period": i['period']
					}
				)
		for i in param['repaymentPlanList']:
			plan_list_pay_type = plan_type[i['repaymentPlanType']]
			plan_list_asset_plan_owner = i['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail4 = GetSqlData.get_user_repayment_detail(
					project_id=r.get("cfq_12_periods_projectId"),
					environment=env,
					period=i['period'],
					repayment_plan_type=plan_list_pay_type
				)
				i.update(
					{
						"sourcePlanId": plan_list_detail4.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail4.get('cur_amount')),
						"payAmount": float(plan_list_detail4.get('rest_amount')),
						"payTime": Common.get_time("-"),
						"period": i['period']
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail5 = GetSqlData.get_repayment_plan_date(project_id=r.get("cfq_12_periods_projectId"),
																	   environment=env,
																	   repayment_plan_type=plan_list_pay_type,
																	   period=i['period'])
				i.update(
					{
						"sourcePlanId": plan_list_detail5.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail5.get('cur_amount')),
						"payAmount": float(plan_list_detail5.get('rest_amount')),
						"payTime": Common.get_time("-"),
						"period": i['period']
					}
				)
		for i in param['feePlanList']:
			plan_list_detail6 = GetSqlData.get_user_repayment_detail(
				project_id=r.get("cfq_12_periods_projectId"),
				environment=env,
				period=i['period'],
				repayment_plan_type=3,
				feecategory=i['feeCategory']
			)
			i.update(
				{
					"sourcePlanId": plan_list_detail6.get('source_plan_id'),
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
			environment=env,
			product="pintec"
		)
		assert rep['resultCode'] == data[0]['msgCode']
		assert rep['content']['message'] == "交易成功"


if __name__ == '__main__':
	pytest.main()
