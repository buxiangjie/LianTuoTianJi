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

logger = Logger(logger="test_nqh_repayment_advance_tp").getlog()


class NqhRepaymentAdvance(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = sys.argv[3]
		cls.r = Common.conn_redis(cls.env)
		cls.file = Config().get_item('File', 'nqh_repayment_advance_case_file')

	@classmethod
	def tearDownClass(cls):
		pass

	def test_0_approved(self):
		"""拿去花进件同意接口"""
		data = excel_table_byname(self.file, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('nqh_repayment_advance', self.env)
		param = json.loads(data[0]['param'])
		self.r.mset(
			{
				"nqh_repayment_advance_sourceProjectId": Common.get_random("sourceProjectId"),
				"nqh_repayment_advance_sourceUserId": Common.get_random("userid"),
				"nqh_repayment_advance_transactionId": "Apollo" + Common.get_random("transactionId"),
				"nqh_repayment_advance_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("nqh_repayment_advance_sourceProjectId"),
				"sourceUserId": self.r.get("nqh_repayment_advance_sourceUserId"),
				"transactionId": self.r.get("nqh_repayment_advance_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": self.r.get("nqh_repayment_advance_cardNum"),
				"custName": self.r.get("nqh_repayment_advance_custName"),
				"phone": self.r.get("nqh_repayment_advance_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": self.r.get("nqh_repayment_advance_phone")})
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
		self.r.set("nqh_repayment_advance_projectId", rep['content']['projectId'])
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	def test_1_loan_notice(self):
		"""拿去花放款通知接口"""
		data = excel_table_byname(self.file, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		self.r.set("nqh_repayment_advance_loan_time", Common.get_time("-"))
		param.update(
			{
				"sourceProjectId": self.r.get("nqh_repayment_advance_sourceProjectId"),
				"sourceUserId": self.r.get("nqh_repayment_advance_sourceUserId"),
				"projectId": self.r.get("nqh_repayment_advance_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("nqh_repayment_advance_cardNum"),
				"bankPhone": self.r.get("nqh_repayment_advance_phone"),
				'loanTime': self.r.get("nqh_repayment_advance_loan_time")
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
			environment=self.env,
			product="pintic"
		)
		print("返回信息:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

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
				"projectId": self.r.get("nqh_repayment_advance_projectId"),
				"sourceProjectId": self.r.get("nqh_repayment_advance_sourceProjectId"),
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
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	def test_3_repayment_one_period(self):
		"""拿去花提前还一期"""
		time.sleep(5)
		data = excel_table_byname(self.file, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			environment=self.env,
			project_id=self.r.get("nqh_repayment_advance_projectId"),
			period=param['repaymentDetailList'][0]['period']
		)
		param['repayment'].update(
			{
				"projectId": self.r.get("nqh_repayment_advance_projectId"),
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
		for i in range(len(param['repaymentDetailList'])):
			plan_pay_type = plan_type.get(param['repaymentDetailList'][i]['repaymentPlanType'])
			repayment_detail = GetSqlData.get_repayment_plan_date(
				project_id=self.r.get("nqh_repayment_advance_projectId"), environment=self.env,
				repayment_plan_type=plan_pay_type, period=param['repaymentDetailList'][i]['period'])
			param['repaymentDetailList'][i].update(
				{
					"sourceRepaymentDetailId": Common.get_random("serviceSn"),
					"sourceCreateTime": Common.get_time("-"),
					"planPayDate": str(repayment_detail.get('plan_pay_date')),
					"thisPayAmount": float(repayment_detail.get('rest_amount')),
					"payTime": Common.get_time("-")
				}
			)
		for y in range(len(param['repaymentPlanList'])):
			plan_pay_type_plan = plan_type.get(param['repaymentPlanList'][y]['repaymentPlanType'])
			repayment_detail_plan = GetSqlData.get_repayment_plan_date(
				project_id=self.r.get("nqh_repayment_advance_projectId"), environment=self.env,
				repayment_plan_type=plan_pay_type_plan, period=param['repaymentPlanList'][y]['period'])
			param['repaymentPlanList'][y].update(
				{
					"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
					"planPayDate": Common.get_time("-"),
					"curAmount": float(repayment_detail_plan.get("rest_amount")),
					"payAmount": float(repayment_detail_plan.get("rest_amount")),
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
			environment=self.env,
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])
		self.assertEqual(rep['content']['message'], "交易成功")
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))


if __name__ == '__main__':
	unittest.main()
