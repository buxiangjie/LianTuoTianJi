#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:翼支付还一期
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

logger = Logger(logger="test_yzf_repayment_tp").getlog()


@allure.feature("翼支付还款流程")
class TestYzfRepayment:
	file = Config().get_item('File', 'yzf_repayment_case_file')
	excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@allure.title("翼支付进件接口")
	@pytest.mark.asset
	def test_0_approved(self, env, r):
		"""翼支付进件同意接口"""
		data = excel_table_byname(self.excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo("yzf_repayment", env)
		r.mset(
			{
				"yzf_repayment_sourceProjectId": Common.get_random("sourceProjectId"),
				"yzf_repayment_sourceUserId": Common.get_random("userid"),
				"yzf_repayment_transactionId": "Apollo" + Common.get_random("transactionId")
			}
		)
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get("yzf_repayment_sourceProjectId"),
				"sourceUserId": r.get("yzf_repayment_sourceUserId"),
				"transactionId": r.get("yzf_repayment_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": r.get("yzf_repayment_cardNum"),
				"custName": r.get("yzf_repayment_custName"),
				"phone": r.get("yzf_repayment_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": r.get("yzf_repayment_phone")})
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		r.set("yzf_repayment_projectId", json.loads(rep.text)['content']['projectId'])
		assert json.loads(rep.text)['resultCode'] == int(data[0]['msgCode'])

	@allure.title("翼支付放款通知接口")
	@pytest.mark.asset
	def test_1_loan_notice(self, env, r):
		"""翼支付放款通知接口"""
		GetSqlData.change_project_audit_status(
			project_id=r.get('yzf_repayment_projectId'),
			enviroment=env
		)
		data = excel_table_byname(self.excel, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get("yzf_repayment_sourceProjectId"),
				"sourceUserId": r.get("yzf_repayment_sourceUserId"),
				"projectId": r.get("yzf_repayment_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": r.get("yzf_repayment_cardNum"),
				"bankPhone": r.get("yzf_repayment_phone"),
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
		print("返回信息:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		assert json.loads(rep.text)['resultCode'] == int(data[0]['msgCode'])

	@allure.title("翼支付放款同步接口")
	@pytest.mark.asset
	def test_2_loanasset(self, env, r):
		"""翼支付进件放款同步接口"""
		global period
		data = excel_table_byname(self.excel, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data("data", "yzf_tp.json")
		repaydate = Common.get_repaydate(24)
		param['asset'].update(
			{
				"projectId": r.get("yzf_repayment_projectId"),
				"sourceProjectId": r.get("yzf_repayment_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": repaydate[0],
				"lastRepaymentDate": repaydate[-1],
				"loanTime": Common.get_time("-")
			}
		)
		for i in range(96):
			param['repaymentPlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": repaydate[param['repaymentPlanList'][i]['period'] - 1]
				}
			)
		for i in range(48):
			param['feePlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": repaydate[param['feePlanList'][i]['period'] - 1]
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		assert json.loads(rep.text)['resultCode'] == int(data[0]['msgCode'])

	@allure.title("翼支付还款接口")
	@pytest.mark.asset
	def test_3_repayment_one_period(self, env, r):
		"""翼支付还款一期"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_user_repayment_amount(
			enviroment=env,
			project_id=r.get("yzf_repayment_projectId"),
			period=param['repaymentDetailList'][0]['period']
		)
		param['repayment'].update(
			{
				"projectId": r.get("yzf_repayment_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
				"successAmount": success_amount
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2",
			"Fee": "3"
		}
		repaydate = Common.get_repaydate(24)
		for i in range(len(param['repaymentDetailList'])):
			plan_pay_type = plan_type[param['repaymentDetailList'][i]['repaymentPlanType']]
			plan_catecory = param['repaymentDetailList'][i]['planCategory']
			asset_plan_owner = param['repaymentDetailList'][i]['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=r.get("yzf_repayment_projectId"),
						enviroment=env,
						period=param['repaymentDetailList'][i]['period'],
						repayment_plan_type=plan_pay_type
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(repayment_detail.get('plan_pay_date')),
							"thisPayAmount": float(repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-")
						}
					)
				else:
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=r.get("yzf_repayment_projectId"),
						enviroment=env,
						period=param['repaymentDetailList'][i]['period'],
						repayment_plan_type=3,
						feecategory=param['repaymentDetailList'][i]['planCategory']
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": repaydate[0].split(" ")[0],
							"thisPayAmount": float(plan_list_detail.get('rest_amount')),
							"payTime": Common.get_time("-")
						}
					)
			elif asset_plan_owner == "financePartner":
				user_repayment_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("yzf_repayment_projectId"),
					enviroment=env,
					period=param['repaymentDetailList'][i]['period'],
					repayment_plan_type=plan_pay_type
				)
				param['repaymentDetailList'][i].update(
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
		for i in range(len(param['repaymentPlanList'])):
			plan_list_pay_type = plan_type[param['repaymentPlanList'][i]['repaymentPlanType']]
			plan_list_asset_plan_owner = param['repaymentPlanList'][i]['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("yzf_repayment_projectId"),
					enviroment=env,
					period=param['repaymentPlanList'][i]['period'],
					repayment_plan_type=plan_list_pay_type
				)
				param['repaymentPlanList'][i].update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail.get("rest_amount")),
						"payAmount": float(plan_list_detail.get("rest_amount")),
						"payTime": Common.get_time("-")
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail = GetSqlData.get_repayment_detail(
					project_id=r.get("yzf_repayment_projectId"),
					enviroment=env,
					period=param['repaymentPlanList'][i]['period'],
					repayment_plan_type=plan_list_pay_type
				)
				param['repaymentPlanList'][i].update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail.get("rest_amount")),
						"payAmount": float(plan_list_detail.get("rest_amount")),
						"payTime": Common.get_time("-")
					}
				)
		for i in range(len(param['feePlanList'])):
			plan_list_detail = GetSqlData.get_user_repayment_detail(
				project_id=r.get("yzf_repayment_projectId"),
				enviroment=env,
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
			enviroment=env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		assert json.loads(rep.text)['resultCode'] == data[0]['msgCode']
		assert json.loads(rep.text)['content']['message'] == "交易成功"


if __name__ == '__main__':
	pytest.main()
