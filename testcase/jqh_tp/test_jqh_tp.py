#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:借去花流程
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

logger = Logger(logger="test_jqh_tp").getlog()

@allure.feature("借去花")
@pytest.mark.skip("业务暂停")
class TestJqh:
	file = Config().get_item('File', 'jqh_case_file')

	@allure.title("借去花进件")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_0_approved(self, r, env):
		"""借去花进件同意接口"""
		data = excel_table_byname(self.file, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		Common.p2p_get_userinfo("jqh", env)
		r.mset(
			{
				"jqh_sourceProjectId": Common.get_random("sourceProjectId"),
				"jqh_sourceUserId": Common.get_random("userid"),
				"jqh_transactionId": "Apollo" + Common.get_random("transactionId"),
				"jqh_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": r.get("jqh_sourceProjectId"),
				"sourceUserId": r.get("jqh_sourceUserId"),
				"transactionId": r.get("jqh_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": r.get("jqh_cardNum"),
				"custName": r.get("jqh_custName"),
				"phone": r.get("jqh_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": r.get("jqh_phone")})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			environment=env,
			product="pintic"
		)
		r.set("jqh_projectId", rep['content']['projectId'])
		assert (int(data[0]['msgCode']), rep['resultCode'])
		assert (rep['content']['message'], "交易成功")
		GetSqlData.change_project_audit_status(
			project_id=r.get('jqh_projectId'),
			environment=env
		)

	@allure.title("借去花放款")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_1_loan(self, r, env):
		"""借去花放款接口"""
		data = excel_table_byname(self.file, 'loan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get("jqh_sourceProjectId"),
				"sourceUserId": r.get("jqh_sourceUserId"),
				"projectId": r.get("jqh_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": r.get("jqh_cardNum"),
				"bankPhone": r.get("jqh_phone")
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
			product="pintic"
		)
		assert (int(data[0]['msgCode']), rep['resultCode'])
		assert (rep['content']['message'], "交易成功")

	@allure.title("借去花放款同步")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_2_loanasset(self, r, env):
		"""借去花进件放款同步接口"""
		time.sleep(10)
		data = excel_table_byname(self.file, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['asset'].update(
			{
				"projectId": r.get("jqh_projectId"),
				"sourceProjectId": r.get("jqh_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": Common.get_repaydate(6)[0],
				"lastRepaymentDate": Common.get_repaydate(6)[-1],
				"loanTime": Common.get_time("-")
			}
		)
		for i in range(0, len(param['repaymentPlanList'])):
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
			environment=env,
			product="pintic"
		)
		assert (int(data[0]['msgCode']), rep['resultCode'])
		assert (rep['content']['message'], "交易成功")

	@allure.title("借去花代偿")
	@allure.severity("blocker")
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_3_compensation(self, r, env):
		"""借去花代偿一期"""
		data = excel_table_byname(self.file, 'compensation')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": r.get("jqh_projectId"),
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": r['jqh_sourceProjectId'],
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
				plan_list_detail = GetSqlData.get_repayment_plan_date(project_id=r.get("jqh_projectId"),
																	  environment=env,
																	  repayment_plan_type=plan_pay_type.get(
																		  i['repaymentPlanType']), period=i['period'])
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("jqh_projectId"),
					environment=env,
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
			environment=env,
			product="pintic"
		)
		assert (rep['resultCode'], data[0]['msgCode'])

	@allure.title("借去花代偿后还款")
	@allure.severity("blocker")
	@pytest.mark.comp_repay
	def test_4_after_comp_repay(self, r, env):
		"""借去花代偿后还款"""
		# noinspection PyGlobalUndefined
		global period, plan_pay_type, plan_list_detail
		data = excel_table_byname(self.file, 'after_comp_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": r.get("jqh_projectId"),
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
					repayment_detail = GetSqlData.get_repayment_plan_date(project_id=r.get("jqh_projectId"),
																		  environment=env,
																		  repayment_plan_type=plan_pay_type,
																		  period=period)
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
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=r.get("jqh_projectId"),
						environment=env,
						period=period,
						repayment_plan_type=3,
						feecategory=param['repaymentDetailList'][i]['planCategory']
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
			elif asset_plan_owner == "financePartner":
				if plan_catecory == 1 or plan_catecory == 2:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=r.get("jqh_projectId"),
						environment=env,
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
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("jqh_projectId"),
					environment=env,
					period=period,
					repayment_plan_type=3,
					feecategory=param['repaymentDetailList'][i]['planCategory']
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
					project_id=r.get("jqh_projectId"),
					environment=env,
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
				plan_list_detail = GetSqlData.get_repayment_plan_date(project_id=r.get("jqh_projectId"),
																	  environment=env,
																	  repayment_plan_type=plan_list_pay_type,
																	  period=param['repaymentPlanList'][i]['period'])
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
			plan_list_detail = GetSqlData.get_user_repayment_detail(
				project_id=r.get("jqh_projectId"),
				environment=env,
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
			data=json.dumps(param, ensure_ascii=False),
			environment=env,
			product="pintic"
		)
		assert (rep['resultCode'], data[0]['msgCode'])
		assert (rep['content']['message'], "交易成功")


if __name__ == '__main__':
	pytest.main()
