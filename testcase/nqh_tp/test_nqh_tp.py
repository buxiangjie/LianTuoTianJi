#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:拿去花流程
"""
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

logger = Logger(logger="test_nqh_tp").getlog()


@allure.feature("拿去花流程")
class TestNqhTp:
	file = Config().get_item('File', 'nqh_case_file')
	excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@allure.title("拿去花进件")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_0_approved(self, env, r):
		"""拿去花进件同意接口"""
		data = excel_table_byname(self.excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		Common.p2p_get_userinfo("nqh", env)
		r.mset(
			{
				"nqh_sourceProjectId": Common.get_random("sourceProjectId"),
				"nqh_sourceUserId": Common.get_random("userid"),
				"nqh_transactionId": Common.get_random("transactionId")
			}
		)
		param.update(
			{
				"sourceProjectId": r.get("nqh_sourceProjectId"),
				"sourceUserId": r.get("nqh_sourceUserId"),
				"transactionId": r.get("nqh_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": r.get("nqh_cardNum"),
				"custName": r.get("nqh_custName"),
				"phone": r.get("nqh_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": r.get("nqh_phone")})
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
		r.set("nqh_projectId", rep['content']['projectId'])
		assert rep['resultCode'] == int(data[0]['msgCode'])
		GetSqlData.change_project_audit_status(
			project_id=r.get('nqh_projectId'),
			enviroment=env
		)

	@allure.title("拿去花放款通知")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_1_loan_notice(self, env, r):
		"""拿去花放款通知接口"""
		data = excel_table_byname(self.excel, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get("nqh_sourceProjectId"),
				"sourceUserId": r.get("nqh_sourceUserId"),
				"projectId": r.get("nqh_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": r.get("nqh_cardNum"),
				"bankPhone": r.get("nqh_phone"),
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
			data=json.dumps(param, ensure_ascii=False),
			enviroment=env,
			product="pintic"
		)
		assert rep['resultCode'] == int(data[0]['msgCode'])

	@allure.title("拿去花放款同步")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_2_loan_asset(self, env, r):
		"""拿去花进件放款同步接口"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['asset'].update(
			{
				"projectId": r.get("nqh_projectId"),
				"sourceProjectId": r.get("nqh_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": Common.get_repaydate(6)[0],
				"lastRepaymentDate": Common.get_repaydate(6)[-1],
				"loanTime": Common.get_time("-")
			}
		)
		for i in range(len(param['repaymentPlanList'])):
			param['repaymentPlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": Common.get_repaydate(6)[param['repaymentPlanList'][i]['period'] - 1]
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

	@allure.title("拿去花代偿")
	@allure.severity("blocker")
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_3_compensation(self, env, r):
		"""拿去花代偿一期"""
		data = excel_table_byname(self.excel, 'compensation')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": r['nqh_projectId'],
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": r['nqh_sourceProjectId'],
					"sourceDetailId": Common.get_random("serviceSn"),
					"sourceSwapId": Common.get_random("serviceSn"),
					"sourceRelatedPlanId": Common.get_random("serviceSn"),
					"actionTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-")
				}
			)
		for i in param['repaymentPlanList']:
			# noinspection PyGlobalUndefined
			global plan_list_detail, plan_pay_type
			plan_pay_type = {
				"Principal": "1",
				"Interest": "2"
			}
			if i['assetPlanOwner'] == "foundPartner":
				plan_list_detail = GetSqlData.get_repayment_detail(
					project_id=r['nqh_projectId'],
					enviroment=env,
					period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType'])
				)
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r['nqh_projectId'],
					enviroment=env,
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
			enviroment=env,
			product="pintic"
		)
		assert rep['resultCode'] == data[0]['msgCode']

	@allure.title("拿去花代偿后还款")
	@allure.severity("blocker")
	@pytest.mark.comp_repay
	def test_4_after_comp_repay(self, env, r):
		"""拿去花代偿后还款"""
		# noinspection PyGlobalUndefined
		global period, plan_pay_type, plan_list_detail
		data = excel_table_byname(self.excel, 'after_comp_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": r['nqh_projectId'],
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
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=r['nqh_projectId'],
						enviroment=env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"relatedPlanId": repayment_detail['source_plan_id'],
							"planPayDate": str(repayment_detail.get('plan_pay_date')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				else:
					fee_detail = GetSqlData.get_user_repayment_detail(
						project_id=r['nqh_projectId'],
						enviroment=env,
						period=period,
						repayment_plan_type=plan_type,
						feecategory=plan_catecory
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"relatedPlanId": fee_detail['source_plan_id'],
							"planPayDate": str(fee_detail['plan_pay_date']),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			elif asset_plan_owner == "financePartner":
				if i['planCategory'] == 3002:
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": Common.get_time("-"),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				else:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=r['nqh_projectId'],
						enviroment=env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(user_repayment_detail.get('plan_pay_date')),
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
					project_id=r['nqh_projectId'],
					enviroment=env,
					period=period,
					repayment_plan_type=plan_list_pay_type
				)
				i.update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": str(plan_list_detail.get('plan_pay_date')),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail = GetSqlData.get_repayment_detail(
					project_id=r['nqh_projectId'],
					enviroment=env,
					period=i['period'],
					repayment_plan_type=plan_list_pay_type
				)
				i.update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": str(plan_list_detail.get('plan_pay_date')),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in param['feePlanList']:
			if i['feeCategory'] != 3001:
				user_fee = GetSqlData.get_repayment_detail(
					project_id=r.get("nqh_projectId"),
					enviroment=env,
					period=i['period'],
					repayment_plan_type=1,
				)
				i.update(
					{
						"sourcePlanId": user_fee['source_plan_id'],
						"planPayDate": str(user_fee['plan_pay_date']),
						"payTime": Common.get_time("-")
					}
				)
			else:
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("nqh_projectId"),
					enviroment=env,
					period=i['period'],
					repayment_plan_type=3,
					feecategory=i['feeCategory']
				)
				i.update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": str(plan_list_detail.get('plan_pay_date')),
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
		assert rep['resultCode'] == data[0]['msgCode']
		assert rep['content']['message'] == "交易成功"


if __name__ == '__main__':
	pytest.main()
