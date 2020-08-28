#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:拿去花还一期
"""
import unittest
import os
import json
import time
import sys
import allure
import pytest

from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = Logger(logger="test_nqh_repayment_tp").getlog()

@allure.feature("拿去花还款")
class TestNqhRepayment:
	file = Config().get_item('File', 'nqh_repayment_case_file')
	excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@allure.title("拿去花进件")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	def test_0_approved(self, env, r):
		"""拿去花进件同意接口"""
		data = excel_table_byname(self.excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo("nqh_repayment", env)
		param = json.loads(data[0]['param'])
		r.mset(
			{
				"nqh_repayment_sourceProjectId": Common.get_random("sourceProjectId"),
				"nqh_repayment_sourceUserId": Common.get_random("userid"),
				"nqh_repayment_transactionId": "Apollo" + Common.get_random("transactionId")
			}
		)
		param.update(
			{
				"sourceProjectId": r.get("nqh_repayment_sourceProjectId"),
				"sourceUserId": r.get("nqh_repayment_sourceUserId"),
				"transactionId": r.get("nqh_repayment_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": r.get("nqh_repayment_cardNum"),
				"custName": r.get("nqh_repayment_custName"),
				"phone": r.get("nqh_repayment_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": r.get("nqh_repayment_phone")})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			enviroment=env,
			product="pintic"
		)
		r.set("nqh_repayment_projectId", rep['content']['projectId'])
		assert rep['resultCode'] == int(data[0]['msgCode'])

	@allure.title("拿去花放款通知")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	def test_1_loan_notice(self, env, r):
		"""拿去花放款通知接口"""
		GetSqlData.change_project_audit_status(
			project_id=r["nqh_repayment_projectId"],
			enviroment=env
		)
		data = excel_table_byname(self.excel, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get("nqh_repayment_sourceProjectId"),
				"sourceUserId": r.get("nqh_repayment_sourceUserId"),
				"projectId": r.get("nqh_repayment_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": r.get("nqh_repayment_cardNum"),
				"bankPhone": r.get("nqh_repayment_phone"),
				'loanTime': Common.get_time("-")
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
			enviroment=env,
			product="pintic"
		)
		assert rep['resultCode'] == int(data[0]['msgCode'])

	@allure.title("拿去花放款同步")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	def test_2_loan_asset(self, env, r):
		"""拿去花进件放款同步接口"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		repaymentdate = Common.get_repaydate(6)
		param['asset'].update(
			{
				"projectId": r.get("nqh_repayment_projectId"),
				"sourceProjectId": r.get("nqh_repayment_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": repaymentdate[0],
				"lastRepaymentDate": repaymentdate[-1],
				"loanTime": Common.get_time("-")
			}
		)
		for i in range(len(param['repaymentPlanList'])):
			param['repaymentPlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": repaymentdate[param['repaymentPlanList'][i]['period'] - 1]
				}
			)
		for i in range(len(param['feePlanList'])):
			param['feePlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": repaymentdate[param['feePlanList'][i]['period'] - 1]
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
			enviroment=env,
			product="pintic"
		)
		assert rep['resultCode'] == int(data[0]['msgCode'])

	@allure.title("拿去花还款推送")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_3_repayment_one_period(self, env, r):
		"""拿去花还款一期"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": r.get("nqh_repayment_projectId"),
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
		for i in range(len(param['repaymentDetailList'])):
			plan_pay_type = plan_type[param['repaymentDetailList'][i]['repaymentPlanType']]
			plan_catecory = param['repaymentDetailList'][i]['planCategory']
			asset_plan_owner = param['repaymentDetailList'][i]['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=r.get("nqh_repayment_projectId"),
						enviroment=env,
						period=period,
						repayment_plan_type=plan_pay_type
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
				else:
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": Common.get_time("-"),
							"payTime": Common.get_time("-")
						}
					)
			elif asset_plan_owner == "financePartner":
				user_repayment_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("nqh_repayment_projectId"),
					enviroment=env,
					period=period,
					repayment_plan_type=plan_pay_type
				)
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": Common.get_time("-"),
						"planPayDate": str(user_repayment_detail.get('plan_pay_date')),
						"payTime": Common.get_time("-")
					}
				)
			else:
				pass
		for i in range(len(param['repaymentPlanList'])):
			plan_list_pay_type = plan_type[param['repaymentPlanList'][i]['repaymentPlanType']]
			plan_list_asset_plan_owner = param['repaymentPlanList'][i]['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("nqh_repayment_projectId"),
					enviroment=env,
					period=param['repaymentPlanList'][i]['period'],
					repayment_plan_type=plan_list_pay_type
				)
				param['repaymentPlanList'][i].update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"payTime": Common.get_time("-")
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail = GetSqlData.get_repayment_detail(
					project_id=r.get("nqh_repayment_projectId"),
					enviroment=env,
					period=param['repaymentPlanList'][i]['period'],
					repayment_plan_type=plan_list_pay_type
				)
				param['repaymentPlanList'][i].update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"payTime": Common.get_time("-")
					}
				)
		for i in range(len(param['feePlanList'])):
			param['feePlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("serviceSn"),
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
			enviroment=env,
			product="pintic"
		)
		assert rep['content']['message'] == "交易成功"
		assert rep['resultCode'] == int(data[0]['msgCode'])


if __name__ == '__main__':
	pytest.main()
