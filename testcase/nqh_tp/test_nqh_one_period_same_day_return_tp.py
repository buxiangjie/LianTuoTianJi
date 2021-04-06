#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:拿去花一期当天全部退货
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

logger = Logger(logger="nqh_one_period_same_day_return_tp").getlog()


@allure.feature("拿去花一期当天全部退货")
@pytest.mark.skip("业务暂停")
class TestNqhOnePeriodSameDayReturn:
	file = Config().get_item('File', 'nqh_one_period_same_day_return_case_file')

	@allure.title("拿去花进件")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_0_approved(self, env, r):
		"""拿去花进件同意接口"""
		data = excel_table_byname(self.file, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('nqh_one_period_same_day_return', env)
		param = json.loads(data[0]['param'])
		r.mset(
			{
				"nqh_one_period_same_day_return_sourceProjectId": Common.get_random("sourceProjectId"),
				"nqh_one_period_same_day_return_sourceUserId": Common.get_random("userid"),
				"nqh_one_period_same_day_return_transactionId": "Apollo" + Common.get_random("transactionId"),
				"nqh_one_period_same_day_return_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": r.get("nqh_one_period_same_day_return_sourceProjectId"),
				"sourceUserId": r.get("nqh_one_period_same_day_return_sourceUserId"),
				"transactionId": r.get("nqh_one_period_same_day_return_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": r.get("nqh_one_period_same_day_return_cardNum"),
				"custName": r.get("nqh_one_period_same_day_return_custName"),
				"phone": r.get("nqh_one_period_same_day_return_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": r.get("nqh_one_period_same_day_return_phone")})
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
		r.set("nqh_one_period_same_day_return_projectId", rep['content']['projectId'])
		assert rep['resultCode'] == int(data[0]['msgCode'])

	@allure.title("拿去花放款通知")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_1_loan_notice(self, env, r):
		"""拿去花放款通知接口"""
		data = excel_table_byname(self.file, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		GetSqlData.change_project_audit_status(
			project_id=r["nqh_one_period_same_day_return_projectId"],
			environment=env
		)
		param = json.loads(data[0]['param'])
		r.set("nqh_one_period_same_day_return_loan_time", Common.get_time("-"))
		param.update(
			{
				"sourceProjectId": r.get("nqh_one_period_same_day_return_sourceProjectId"),
				"sourceUserId": r.get("nqh_one_period_same_day_return_sourceUserId"),
				"projectId": r.get("nqh_one_period_same_day_return_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": r.get("nqh_one_period_same_day_return_cardNum"),
				"bankPhone": r.get("nqh_one_period_same_day_return_phone"),
				'loanTime': r.get("nqh_one_period_same_day_return_loan_time")
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

	@allure.title("拿去花放款同步")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_2_loan_asset(self, env, r):
		"""拿去花进件放款同步接口"""
		# noinspection PyGlobalUndefined
		global period
		time.sleep(5)
		data = excel_table_byname(self.file, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		if len(param['repaymentPlanList']) / 2 == 2:
			period = 1
		elif len(param['repaymentPlanList']) / 2 == 6:
			period = 3
		elif len(param['repaymentPlanList']) / 2 == 12:
			period = 6
		elif len(param['repaymentPlanList']) / 2 == 18:
			period = 9
		elif len(param['repaymentPlanList']) / 2 == 24:
			period = 12
		param['asset'].update(
			{
				"projectId": r.get("nqh_one_period_same_day_return_projectId"),
				"sourceProjectId": r.get("nqh_one_period_same_day_return_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": Common.get_repaydate(period=period)[0],
				"lastRepaymentDate": Common.get_repaydate(period=period)[-1],
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

	@allure.title("拿去花当天全部退货")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_3_repayment_one_period(self, env, r):
		"""拿去花一期当天全部退货"""
		time.sleep(5)
		data = excel_table_byname(self.file, 'same_day_return')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_all_repayment_amount(
			environment=env,
			project_id=r.get("nqh_one_period_same_day_return_projectId"))
		param['repayment'].update(
			{
				"projectId": r.get("nqh_one_period_same_day_return_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
				"successAmount": success_amount
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2"
		}

		for i in param['repaymentDetailList']:
			plan_pay_type = plan_type.get(i['repaymentPlanType'])
			repayment_detail = GetSqlData.get_repayment_detail(
				project_id=r.get("nqh_one_period_same_day_return_projectId"),
				environment=env, period=i['period'],
				repayment_plan_type=plan_pay_type)
			i.update(
				{
					"sourceRepaymentDetailId": Common.get_random("serviceSn"),
					"sourceCreateTime": Common.get_time("-"),
					"payTime": Common.get_time("-"),
					"thisPayAmount": float(repayment_detail.get('rest_amount')),
					"planPayDate": str(repayment_detail.get('plan_pay_date'))
				}
			)
		for y in param['repaymentPlanList']:
			plan_pay_type_plan = plan_type.get(y['repaymentPlanType'])
			repayment_detail_plan = GetSqlData.get_repayment_detail(
				project_id=r.get("nqh_one_period_same_day_return_projectId"),
				environment=env, period=y['period'],
				repayment_plan_type=plan_pay_type_plan)
			if plan_pay_type_plan == '1':
				y.update(
					{
						"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
						"curAmount": float(repayment_detail_plan.get("rest_amount")),
						"payAmount": float(repayment_detail_plan.get("rest_amount")),
						"payTime": Common.get_time("-"),
						"planPayDate": str(repayment_detail_plan.get("plan_pay_date"))
					}
				)
			elif plan_pay_type_plan == '2':
				y.update(
					{
						"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
						"payTime": Common.get_time("-"),
						"planPayDate": str(repayment_detail_plan.get("plan_pay_date"))
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

	@allure.title("拿去花退货更新还款计划")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_4_repayment_after_return(self, env, r):
		"""退货更新还款计划"""
		time.sleep(5)
		data = excel_table_byname(self.file, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		plan_type = {
			"Principal": "1",
			"Interest": "2"
		}
		repayment = GetSqlData.get_repayment_detail(
			project_id=r.get("nqh_one_period_same_day_return_projectId"),
			environment=env,
			period=1,
			repayment_plan_type="1"
		)

		success_amount = GetSqlData.get_repayment_amount(
			project_id=r.get("nqh_one_period_same_day_return_projectId"),
			environment=env, period=1
		)
		param['repayment'].update(
			{
				"projectId": r.get("nqh_one_period_same_day_return_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": str(repayment.get('plan_pay_date')),
				"sourceCreateTime": str(repayment.get('plan_pay_date')),
				"successAmount": success_amount
			}
		)
		for i in param['repaymentDetailList']:
			plan_pay_type = plan_type.get(i['repaymentPlanType'])
			repayment_detail = GetSqlData.get_repayment_detail(
				project_id=r.get("nqh_one_period_same_day_return_projectId"),
				environment=env, period=1,
				repayment_plan_type=plan_pay_type)
			i.update(
				{
					"sourceRepaymentDetailId": Common.get_random("serviceSn"),
					"sourceCreateTime": Common.get_time("-"),
					"planPayDate": str(repayment_detail.get('plan_pay_date')),
					"thisPayAmount": float(repayment_detail.get('cur_amount')),
					"payTime": Common.get_time("-")
				}
			)

		for y in param['repaymentPlanList']:
			plan_pay_type_plan = plan_type.get(y['repaymentPlanType'])
			repayment_detail_plan = GetSqlData.get_repayment_detail(
				project_id=r.get("nqh_one_period_same_day_return_projectId"),
				environment=env, period=y['period'],
				repayment_plan_type=plan_pay_type_plan)
			y.update(
				{
					"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
					"curAmount": float(repayment_detail_plan.get('origin_amount')),
					"payAmount": float(repayment_detail_plan.get('origin_amount')),
					"payTime": Common.get_time('-')
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


if __name__ == '__main__':
	pytest.main()
