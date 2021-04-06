#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe: 翼支付提前结清
"""
import unittest
import os
import json
import time
import sys
import pytest
import allure

from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = Logger(logger="test_yzf_repayment_advance_tp").getlog()


@allure.feature("翼支付提前结清")
@pytest.mark.skip("业务暂停")
class TestYzfRepaymentAdvance:
	file = Config().get_item('File', 'yzf_repayment_advance_case_file')

	@allure.title("翼支付进件")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_0_approved(self, r, env):
		"""翼支付进件同意接口"""
		data = excel_table_byname(self.file, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('yzf_repayment_advance', env)
		param = json.loads(data[0]['param'])
		r.mset(
			{
				"yzf_repayment_advance_sourceProjectId": Common.get_random("sourceProjectId"),
				"yzf_repayment_advance_sourceUserId": Common.get_random("userid"),
				"yzf_repayment_advance_transactionId": "Apollo" + Common.get_random("transactionId")
			}
		)
		param.update(
			{
				"sourceProjectId": r.get("yzf_repayment_advance_sourceProjectId"),
				"sourceUserId": r.get("yzf_repayment_advance_sourceUserId"),
				"transactionId": r.get("yzf_repayment_advance_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": r.get("yzf_repayment_advance_cardNum"),
				"custName": r.get("yzf_repayment_advance_custName"),
				"phone": r.get("yzf_repayment_advance_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": r.get("yzf_repayment_advance_phone")})
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
		r.set("yzf_repayment_advance_projectId", rep['content']['projectId'])
		assert rep['resultCode'] == int(data[0]['msgCode'])
		GetSqlData.change_project_audit_status(r['yzf_repayment_advance_projectId'], env)

	@allure.title("翼支付放款通知")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_1_loan_notice(self, r, env):
		"""翼支付放款通知接口"""
		data = excel_table_byname(self.file, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		r["yzf_repayment_advance_loan_time"] = Common.get_time("-")
		param.update(
			{
				"sourceProjectId": r.get("yzf_repayment_advance_sourceProjectId"),
				"sourceUserId": r.get("yzf_repayment_advance_sourceUserId"),
				"projectId": r.get("yzf_repayment_advance_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": r.get("yzf_repayment_advance_cardNum"),
				"bankPhone": r.get("yzf_repayment_advance_phone"),
				"loanTime": r.get("yzf_repayment_advance_loan_time")
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
			environment=env,
			product="pintic"
		)
		assert rep['resultCode'] == int(data[0]['msgCode'])

	@allure.title("翼支付进件放款同步")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_2_loanasset(self, r, env):
		"""翼支付进件放款同步接口"""
		data = excel_table_byname(self.file, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		if len(param['repaymentPlanList']) / 2 == 6:
			period = 3
		elif len(param['repaymentPlanList']) / 2 == 12:
			period = 6
		elif len(param['repaymentPlanList']) / 2 == 18:
			period = 9
		elif len(param['repaymentPlanList']) / 2 == 24:
			period = 12
		param['asset'].update(
			{
				"projectId": r.get("yzf_repayment_advance_projectId"),
				"sourceProjectId": r.get("yzf_repayment_advance_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": Common.get_repaydate(period)[0],
				"lastRepaymentDate": Common.get_repaydate(period)[-1],
				"loanTime": Common.get_time("-")
			}
		)
		for i in range(period * 4):
			param['repaymentPlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": Common.get_repaydate(period)[param['repaymentPlanList'][i]['period'] - 1]
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
		assert rep['resultCode'] == int(data[0]['msgCode'])

	@allure.title("翼支付提前结清")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_3_repayment_settle_in_advance(self, r, env):
		"""翼支付提前结清"""
		data = excel_table_byname(self.file, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = Common().get_json_data('data', 'yzf_settle_in_advance.json')
		param['repayment'].update(
			{
				"projectId": r.get("yzf_repayment_advance_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
				"successAmount": 103.36
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
					"sourceCreateTime": Common.get_time("-")
				}
			)
			if i['repaymentPlanType'] == 'Principal':
				this_pay_amount = GetSqlData.get_all_repayment_amount(
					environment=env,
					project_id=r.get("yzf_repayment_advance_projectId")
				)
				i.update(
					{
						"thisPayAmount": this_pay_amount
					}
				)
		for i in param['repaymentPlanList']:
			i.update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"payTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-")
				}
			)
			if i['repaymentStatus'] == 'repayment_done':
				i.update(
					{
						"curAmount": GetSqlData.get_all_repayment_amount(
							environment=env,
							project_id=r.get("yzf_repayment_advance_projectId")
						),
						"payAmount": GetSqlData.get_all_repayment_amount(
							environment=env,
							project_id=r.get("yzf_repayment_advance_projectId")
						)
					}
				)
			else:
				if i['assetPlanOwner'] == 'financePartner':
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=r.get("yzf_repayment_advance_projectId"),
						environment=env, period=i['period'],
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
						project_id=r.get("yzf_repayment_advance_projectId"),
						environment=env, period=i['period'],
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
		assert rep['resultCode'] == data[0]['msgCode']
		assert rep['content']['message'] == "交易成功"
		assert rep['resultCode'] == int(data[0]['msgCode'])


if __name__ == '__main__':
	pytest.main()
