#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:
"""
import os
import json
import sys
import allure
import pytest

from config.configer import Config
from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = Logger(logger="test_yzf_tp").getlog()


@allure.feature("翼支付流程")
class TestYzfTp:
	file = Config().get_item('File', 'yzf_case_file')
	excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@allure.title("翼支付进件接口")
	@pytest.mark.asset
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_0_approved(self, env, r):
		"""翼支付进件同意接口"""
		data = excel_table_byname(self.excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('yzf', env)
		param = json.loads(data[0]['param'])
		r.mset(
			{
				"yzf_sourceUserId": Common.get_random('userid'),
				"yzf_transactionId": Common.get_random('transactionId'),
				"yzf_phone": Common.get_random('phone'),
				"yzf_sourceProjectId": Common.get_random('sourceProjectId'),
			}
		)
		param.update(
			{
				"sourceProjectId": r.get("yzf_sourceProjectId"),
				"sourceUserId": r.get("yzf_sourceUserId"),
				"transactionId": r.get("yzf_transactionId")
			}
		)

		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": r.get("yzf_cardNum"),
				"custName": r.get("yzf_custName"),
				"phone": r.get("yzf_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": r.get("yzf_phone")})
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
		r.set("yzf_projectId", json.loads(rep.text)['content']['projectId'])
		assert json.loads(rep.text)['resultCode'] == int(data[0]['msgCode'])
		GetSqlData.change_project_audit_status(
			project_id=r.get('yzf_projectId'),
			enviroment=env
		)

	@allure.title("翼支付放款通知")
	@pytest.mark.asset
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_1_loan_notice(self, r, env):
		"""翼支付放款通知接口"""
		data = excel_table_byname(self.excel, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get("yzf_sourceProjectId"),
				"sourceUserId": r.get("yzf_sourceUserId"),
				"projectId": r.get("yzf_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": r.get("yzf_cardNum"),
				"bankPhone": r.get("yzf_phone"),
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
			enviroment=env,
			product="pintic"
		)
		print("返回信息:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		assert json.loads(rep.text)['resultCode'] == int(data[0]['msgCode'])

	@allure.title("翼支付放款同步")
	@pytest.mark.asset
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_2_loanasset(self, r, env):
		"""翼支付进件放款同步接口"""
		global period
		data = excel_table_byname(self.excel, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data("data", "yzf_tp.json")
		param['asset'].update(
			{
				"projectId": r.get("yzf_projectId"),
				"sourceProjectId": r.get("yzf_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": Common.get_repaydate(24)[0],
				"lastRepaymentDate": Common.get_repaydate(24)[-1],
				"loanTime": Common.get_time("-")
			}
		)

		for i in range(96):
			period = param['repaymentPlanList'][i]['period']
			param['repaymentPlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": Common.get_repaydate(period=period)[period - 1]
				}
			)
		for i in range(48):
			period = param['repaymentPlanList'][i]['period']
			param['feePlanList'][i].update(
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
			enviroment=env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		assert json.loads(rep.text)['resultCode'] == int(data[0]['msgCode'])

	# @unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] == "compensation", "-")
	@allure.title("翼支付代偿")
	@pytest.mark.comp
	@pytest.mark.comp_repay
	def test_3_compensation(self, r, env):
		"""翼支付12期代偿一期"""
		data = excel_table_byname(self.excel, 'compensation')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": r.get("yzf_projectId"),
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": r.get("yzf_sourceProjectId"),
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
					project_id=r.get("yzf_projectId"),
					enviroment=env,
					period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType']),

				)
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("yzf_projectId"),
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		assert json.loads(rep.text)['resultCode'] == data[0]['msgCode']

	# @unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] == "compensation_after_repay", "-")
	@allure.title("翼支付代偿后还款")
	@pytest.mark.comp_repay
	def test_4_after_comp_repay(self, r, env):
		"""翼支付代偿后还款"""
		global period, plan_pay_type, plan_list_detail
		data = excel_table_byname(self.excel, 'after_comp_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": r.get("yzf_projectId"),
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
		fee_3003 = Common.get_random('serviceSn')
		fee_3002 = Common.get_random('serviceSn')
		for i in range(len(param['repaymentDetailList'])):
			plan_pay_type = plan_type[param['repaymentDetailList'][i]['repaymentPlanType']]
			plan_catecory = param['repaymentDetailList'][i]['planCategory']
			asset_plan_owner = param['repaymentDetailList'][i]['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=r.get("yzf_projectId"),
						enviroment=env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"relatedPlanId": plan_list_detail.get("source_plan_id"),
							"planPayDate": str(repayment_detail.get('plan_pay_date')),
							"thisPayAmount": float(repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				elif plan_catecory == 3002:
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=r.get("yzf_projectId"),
						enviroment=env,
						period=period,
						repayment_plan_type=2
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"relatedPlanId": fee_3002,
							"planPayDate": str(repayment_detail.get('plan_pay_date')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				else:
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=r.get("yzf_projectId"),
						enviroment=env,
						period=period,
						repayment_plan_type=plan_pay_type,
						feecategory=param['repaymentDetailList'][i]['planCategory']
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"relatedPlanId": plan_list_detail.get("source_plan_id"),
							"planPayDate": str(plan_list_detail.get("plan_pay_date")),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			elif asset_plan_owner == "financePartner":
				if plan_catecory == 1 or plan_catecory == 2:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=r.get("yzf_projectId"),
						enviroment=env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"relatedPlanId": user_repayment_detail.get("source_plan_id"),
							"planPayDate": str(user_repayment_detail.get('plan_pay_date')),
							"thisPayAmount": float(user_repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				elif param['repaymentDetailList'][i]['planCategory'] == 3003:
					param['repaymentDetailList'][i].update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"relatedPlanId": fee_3003,
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			else:
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("yzf_projectId"),
					enviroment=env,
					period=period,
					repayment_plan_type=3,
					feecategory=param['repaymentDetailList'][i]['planCategory']
				)
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": Common.get_time("-"),
						"relatedPlanId": plan_list_detail.get("source_plan_id"),
						"planPayDate": str(plan_list_detail.get("plan_pay_date")),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in range(len(param['repaymentPlanList'])):
			plan_list_pay_type = plan_type[param['repaymentPlanList'][i]['repaymentPlanType']]
			plan_list_asset_plan_owner = param['repaymentPlanList'][i]['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("yzf_projectId"),
					enviroment=env,
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
					project_id=r.get("yzf_projectId"),
					enviroment=env,
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
		for i in range(len(param['feePlanList'])):
			if param['feePlanList'][i]['feeCategory'] == 3003:
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("yzf_projectId"),
					enviroment=env,
					period=param['feePlanList'][i]['period'],
					repayment_plan_type="3"
				)
				param['feePlanList'][i].update(
					{
						"sourcePlanId": Common.get_random('serviceSn'),
						"planPayDate": str(plan_list_detail.get('plan_pay_date')),
						"payTime": Common.get_time("-")
					}
				)
			elif param['feePlanList'][i]['feeCategory'] == 3002:
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("yzf_projectId"),
					enviroment=env,
					period=param['feePlanList'][i]['period'],
					repayment_plan_type="3"
				)
				param['feePlanList'][i].update(
					{
						"sourcePlanId": Common.get_random('serviceSn'),
						"planPayDate": str(plan_list_detail.get('plan_pay_date')),
						"payTime": Common.get_time("-")
					}
				)
			else:
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=r.get("yzf_projectId"),
					enviroment=env,
					period=param['feePlanList'][i]['period'],
					repayment_plan_type="3",
					feecategory=param['feePlanList'][i]['feeCategory']
				)
				param['feePlanList'][i].update(
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		assert json.loads(rep.text)['resultCode'] == data[0]['msgCode']
		assert json.loads(rep.text)['content']['message'] == "交易成功"


if __name__ == '__main__':
	pytest.main()
