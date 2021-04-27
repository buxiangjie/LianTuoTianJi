#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:借去花还一期
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

logger = Logger(logger="test_jqh_repayment_tp").getlog()

@allure.feature("借去花还款")
@pytest.mark.skip("业务暂停")
class TestJqhRepayment:
	file = Config().get_item('File', 'jqh_repayment_case_file')

	@allure.title("借去花进件")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_0_approved(self, r, env):
		"""借去花进件同意接口"""
		data = excel_table_byname(self.file, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		Common.p2p_get_userinfo("jqh_repayment", env)
		r.mset(
			{
				"jqh_repayment_sourceProjectId": Common.get_random("sourceProjectId"),
				"jqh_repayment_sourceUserId": Common.get_random("userid"),
				"jqh_repayment_transactionId": "Apollo" + Common.get_random("transactionId"),
				"jqh_repayment_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": r.get("jqh_repayment_sourceProjectId"),
				"sourceUserId": r.get("jqh_repayment_sourceUserId"),
				"transactionId": r.get("jqh_repayment_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": r.get("jqh_repayment_cardNum"),
				"custName": r.get("jqh_repayment_custName"),
				"phone": r.get("jqh_repayment_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": r.get("jqh_repayment_phone")})
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
		r.set("jqh_repayment_projectId", rep['content']['projectId'])
		assert (rep['resultCode'], int(data[0]['msgCode']))

	@allure.title("借去花放款")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_1_loan(self, r, env):
		"""借去花放款接口"""
		GetSqlData.change_project_audit_status(
			project_id=r.get("jqh_repayment_projectId"),
			environment=env
		)
		data = excel_table_byname(self.file, 'loan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get("jqh_repayment_sourceProjectId"),
				"sourceUserId": r.get("jqh_repayment_sourceUserId"),
				"projectId": r.get("jqh_repayment_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": r.get("jqh_repayment_cardNum"),
				"bankPhone": r.get("jqh_repayment_phone")
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
		assert (rep['resultCode'], int(data[0]['msgCode']))

	@allure.title("借去花放款同步")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_2_loanasset(self, r, env):
		"""借去花进件放款同步接口"""
		time.sleep(5)
		data = excel_table_byname(self.file, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['asset'].update(
			{
				"projectId": r.get("jqh_repayment_projectId"),
				"sourceProjectId": r.get("jqh_repayment_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": Common.get_repaydate(6)[0],
				"lastRepaymentDate": Common.get_repaydate(6)[-1],
				"loanTime": Common.get_time("-")
			}
		)
		for i in param['repaymentPlanList']:
			i.update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": Common.get_repaydate(6)[i['period'] - 1]
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
		assert (rep['resultCode'], int(data[0]['msgCode']))

	@allure.title("借去花还款一期")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_3_repayment_one_period(self, r, env):
		"""借去花还款一期"""
		data = excel_table_byname(self.file, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		user_amount = GetSqlData.get_user_repayment_amount(
					environment=env,
					project_id=r.get("jqh_repayment_projectId"),
					period=param['repaymentDetailList'][0]['period']
				)
		param['repayment'].update(
			{
				"projectId": r.get("jqh_repayment_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
				"successAmount": user_amount
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2"
		}
		for i in param['repaymentDetailList']:
			plan_pay_type = plan_type[i['repaymentPlanType']]
			plan_catecory = i['planCategory']
			asset_plan_owner = i['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail = GetSqlData.get_repayment_plan_date(project_id=r.get("jqh_repayment_projectId"),
																		  environment=env,
																		  repayment_plan_type=plan_pay_type,
																		  period=i['period'])
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(repayment_detail.get('plan_pay_date')),
							"thisPayAmount": float(repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-")
						}
					)
				else:
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": Common.get_repaydate("1")[0].split(" ")[0],
							"payTime": Common.get_time("-")
						}
					)
			elif asset_plan_owner == "financePartner":
				user_repayment_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("jqh_repayment_projectId"),
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
						"payTime": Common.get_time("-")
					}
				)
			else:
				pass
		for i in param['repaymentPlanList']:
			plan_list_pay_type = plan_type[i['repaymentPlanType']]
			plan_list_asset_plan_owner = i['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("jqh_repayment_projectId"),
					environment=env,
					period=i['period'],
					repayment_plan_type=plan_list_pay_type
				)
				i.update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail.get("rest_amount")),
						"payAmount": float(plan_list_detail.get("rest_amount")),
						"payTime": Common.get_time("-")
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail = GetSqlData.get_repayment_plan_date(project_id=r.get("jqh_repayment_projectId"),
																	  environment=env,
																	  repayment_plan_type=plan_list_pay_type,
																	  period=i['period'])
				i.update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail.get("rest_amount")),
						"payAmount": float(plan_list_detail.get("rest_amount")),
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
		assert (rep['content']['message'], "交易成功")
		assert (rep['resultCode'], int(data[0]['msgCode']))


if __name__ == '__main__':
	pytest.main()
