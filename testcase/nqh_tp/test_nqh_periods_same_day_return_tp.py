#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:
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

logger = Logger(logger="test_nqh_periods_same_day_return_tp").getlog()


class NqhPeriodsSameDayReturn(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = sys.argv[3]
		cls.r = Common.conn_redis(cls.env)
		cls.file = Config().get_item('File', 'nqh_periods_same_day_return_case_file')

	@classmethod
	def tearDownClass(cls):
		pass

	def test_0_approved(self):
		"""拿去花进件同意接口"""
		data = excel_table_byname(self.file, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('nqh_periods_same_day_return', self.env)
		param = json.loads(data[0]['param'])
		self.r.mset(
			{
				"nqh_periods_same_day_return_sourceProjectId": Common.get_random("sourceProjectId"),
				"nqh_periods_same_day_return_sourceUserId": Common.get_random("userid"),
				"nqh_periods_same_day_return_transactionId": "Apollo" + Common.get_random("transactionId"),
				"nqh_periods_same_day_return_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("nqh_periods_same_day_return_sourceProjectId"),
				"sourceUserId": self.r.get("nqh_periods_same_day_return_sourceUserId"),
				"transactionId": self.r.get("nqh_periods_same_day_return_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": self.r.get("nqh_periods_same_day_return_cardNum"),
				"custName": self.r.get("nqh_periods_same_day_return_custName"),
				"phone": self.r.get("nqh_periods_same_day_return_phone")
			}
		)
		param['cardInfo'].update(
			{"bankPhone": self.r.get("nqh_periods_same_day_return_phone")})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			environment=self.env,
			product="pintic"
		)
		self.r.set("nqh_periods_same_day_return_projectId", json.loads(rep.text)['content']['projectId'])
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))

	def test_1_loan_notice(self):
		"""拿去花放款通知接口"""
		data = excel_table_byname(self.file, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('nqh_periods_same_day_return_projectId'),
			environment=self.env
		)
		self.r.set("nqh_periods_same_day_return_loan_time", Common.get_time("-"))
		param.update(
			{
				"sourceProjectId": self.r.get("nqh_periods_same_day_return_sourceProjectId"),
				"sourceUserId": self.r.get("nqh_periods_same_day_return_sourceUserId"),
				"projectId": self.r.get("nqh_periods_same_day_return_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("nqh_periods_same_day_return_cardNum"),
				"bankPhone": self.r.get("nqh_periods_same_day_return_phone"),
				'loanTime': self.r.get("nqh_periods_same_day_return_loan_time")
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
			environment=self.env,
			product="pintic"
		)
		print("返回信息:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))

	def test_2_loan_asset(self):
		"""拿去花进件放款同步接口"""
		global period
		time.sleep(5)
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
				"projectId": self.r.get("nqh_periods_same_day_return_projectId"),
				"sourceProjectId": self.r.get("nqh_periods_same_day_return_sourceProjectId"),
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
			environment=self.env,
			product="pintic"
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))

	def test_3_repayment_one_period(self):
		"""拿去花多期当天部分退货"""
		time.sleep(5)
		data = excel_table_byname(self.file, 'same_day_return')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_all_repayment_amount(
			environment=self.env,
			project_id=self.r.get("nqh_periods_same_day_return_projectId")) - 600
		param['repayment'].update(
			{
				"projectId": self.r.get("nqh_periods_same_day_return_projectId"),
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

		for detail in range(len(param['repaymentDetailList'])):
			param['repaymentDetailList'][detail].update(
				{
					"sourceRepaymentDetailId": Common.get_random("serviceSn"),
					"sourceCreateTime": Common.get_time("-"),
					"payTime": Common.get_time("-"),
					"thisPayAmount": param['repayment']['successAmount']
				}
			)
		for y in range(len(param['repaymentPlanList'])):
			plan_pay_type_plan = plan_type.get(param['repaymentPlanList'][y]['repaymentPlanType'])
			repayment_detail_plan = GetSqlData.get_repayment_detail(
				project_id=self.r.get("nqh_periods_same_day_return_projectId"),
				environment=self.env,
				period=param['repaymentPlanList'][y]['period'],
				repayment_plan_type=plan_pay_type_plan
			)
			if plan_pay_type_plan == "1":
				param['repaymentPlanList'][y].update(
					{
						"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
						"curAmount": "100.00"
					}
				)
			elif plan_pay_type_plan == "2":
				param['repaymentPlanList'][y].update(
					{
						"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
						"curAmount": "10.00"
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
			environment=self.env,
			product="pintic"
		)
		self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])
		self.assertEqual(json.loads(rep.text)['content']['message'], "交易成功")

	def test_4_repayment_after_return(self):
		"""退货更新还款计划"""
		time.sleep(5)
		data = excel_table_byname(self.file, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		for per in range(1, 7):
			plan_type = {
				"Principal": "1",
				"Interest": "2"
			}
			repayment = GetSqlData.get_repayment_detail(
				project_id=self.r.get("nqh_periods_same_day_return_projectId"),
				environment=self.env,
				period=per,
				repayment_plan_type="1"
			)
			success_amount = GetSqlData.get_repayment_amount(
				project_id=self.r.get("nqh_periods_same_day_return_projectId"),
				environment=self.env,
				period=per
			)
			param['repayment'].update(
				{
					"projectId": self.r.get("nqh_periods_same_day_return_projectId"),
					"sourceRepaymentId": Common.get_random("sourceProjectId"),
					"payTime": str(repayment.get('plan_pay_date')),
					"sourceCreateTime": str(repayment.get('plan_pay_date')),
					"successAmount": success_amount
				}
			)
			for i in range(len(param['repaymentDetailList'])):
				plan_pay_type = plan_type.get(param['repaymentDetailList'][i]['repaymentPlanType'])
				repayment_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("nqh_periods_same_day_return_projectId"),
					environment=self.env,
					period=per,
					repayment_plan_type=plan_pay_type
				)
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": str(repayment_detail.get('plan_pay_date')),
						"period": per,
						"planPayDate": str(repayment_detail.get('plan_pay_date')),
						"thisPayAmount": float(repayment_detail.get('rest_amount')),
						"payTime": Common.get_time("-")
					}
				)
			for y in range(len(param['repaymentPlanList'])):
				plan_pay_type_plan = plan_type.get(param['repaymentPlanList'][y]['repaymentPlanType'])
				repayment_detail_plan = GetSqlData.get_repayment_detail(
					project_id=self.r.get("nqh_periods_same_day_return_projectId"),
					environment=self.env,
					period=param['repaymentPlanList'][y]['period'],
					repayment_plan_type=plan_pay_type_plan
				)
				if plan_pay_type_plan == "1":
					param['repaymentPlanList'][y].update(
						{
							"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
							"curAmount": "100.00"
						}
					)
				elif plan_pay_type_plan == "2":
					param['repaymentPlanList'][y].update(
						{
							"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
							"curAmount": "10.00"
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
				environment=self.env,
				product="pintic"
			)

			self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])
			self.assertEqual(json.loads(rep.text)['content']['message'], "交易成功")


if __name__ == '__main__':
	unittest.main()
