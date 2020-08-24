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

logger = Logger(logger="test_nqh_repayment_normal_settle_tp").getlog()


class NqhRepaymentNormalSettle(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = "test"
		cls.r = Common.conn_redis(cls.env)
		file = Config().get_item('File', 'nqh_repayment_normal_settle_case_file')
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@classmethod
	def tearDownClass(cls):
		pass

	def test_0_approved(self):
		"""拿去花进件同意接口"""
		data = excel_table_byname(self.excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('nqh_repayment_normal_settle', self.env)
		param = json.loads(data[0]['param'])
		self.r.mset(
			{
				"nqh_repayment_normal_settle_sourceProjectId": Common.get_random("sourceProjectId"),
				"nqh_repayment_normal_settle_sourceUserId": Common.get_random("userid"),
				"nqh_repayment_normal_settle_transactionId": "Apollo" + Common.get_random("transactionId"),
				"nqh_repayment_normal_settle_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("nqh_repayment_normal_settle_sourceProjectId"),
				"sourceUserId": self.r.get("nqh_repayment_normal_settle_sourceUserId"),
				"transactionId": self.r.get("nqh_repayment_normal_settle_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": self.r.get("nqh_repayment_normal_settle_cardNum"),
				"custName": self.r.get("nqh_repayment_normal_settle_custName"),
				"phone": self.r.get("nqh_repayment_normal_settle_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": self.r.get("nqh_repayment_normal_settle_phone")})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			enviroment=self.env,
			product="pintic"
		)
		self.r.set("nqh_repayment_normal_settle_projectId", rep['content']['projectId'])
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	def test_1_loan_notice(self):
		"""拿去花放款通知接口"""
		data = excel_table_byname(self.excel, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('nqh_repayment_normal_settle_projectId'),
			enviroment=self.env
		)
		param = json.loads(data[0]['param'])
		self.r.set("nqh_repayment_normal_settle_loan_time", Common.get_time("-"))
		param.update(
			{
				"sourceProjectId": self.r.get("nqh_repayment_normal_settle_sourceProjectId"),
				"sourceUserId": self.r.get("nqh_repayment_normal_settle_sourceUserId"),
				"projectId": self.r.get("nqh_repayment_normal_settle_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("nqh_repayment_normal_settle_cardNum"),
				"bankPhone": self.r.get("nqh_repayment_normal_settle_phone"),
				'loanTime': self.r.get("nqh_repayment_normal_settle_loan_time")
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
			enviroment=self.env,
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	def test_2_loan_asset(self):
		"""拿去花进件放款同步接口"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'loan_asset')
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
				"projectId": self.r.get("nqh_repayment_normal_settle_projectId"),
				"sourceProjectId": self.r.get("nqh_repayment_normal_settle_sourceProjectId"),
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
			enviroment=self.env,
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	def test_3_repayment_one_period(self):
		"""拿去花全部结清"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		for per in range(1, 7):
			plan_type = {
				"Principal": "1",
				"Interest": "2"
			}
			repayment = GetSqlData.get_repayment_detail(
				project_id=self.r.get("nqh_repayment_normal_settle_projectId"),
				enviroment=self.env,
				period=per,
				repayment_plan_type="1"
			)
			success_amount = GetSqlData.get_repayment_amount(
				enviroment=self.env,
				project_id=self.r.get("nqh_repayment_normal_settle_projectId"),
				period=per
			)
			param['repayment'].update(
				{
					"projectId": self.r.get("nqh_repayment_normal_settle_projectId"),
					"sourceRepaymentId": Common.get_random("sourceProjectId"),
					"payTime": str(repayment.get('plan_pay_date')),
					"sourceCreateTime": str(repayment.get('plan_pay_date')),
					"successAmount": success_amount
				}
			)
			for i in range(len(param['repaymentDetailList'])):
				plan_pay_type = plan_type.get(param['repaymentDetailList'][i]['repaymentPlanType'])
				repayment_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("nqh_repayment_normal_settle_projectId"),
					enviroment=self.env,
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
						"payTime": str(repayment_detail.get('plan_pay_date'))
					}
				)
			for y in range(len(param['repaymentPlanList'])):
				plan_pay_type_plan = plan_type.get(param['repaymentPlanList'][y]['repaymentPlanType'])
				if param['repaymentPlanList'][y]['assetPlanOwner'] == 'foundPartner':
					repayment_detail_plan = GetSqlData.get_repayment_detail(
						project_id=self.r.get("nqh_repayment_normal_settle_projectId"),
						enviroment=self.env,
						period=per,
						repayment_plan_type=plan_pay_type_plan
					)
					param['repaymentPlanList'][y].update(
						{
							"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
							"planPayDate": str(repayment_detail_plan.get('plan_pay_date')),
							"curAmount": float(repayment_detail_plan.get("rest_amount")),
							"payAmount": float(repayment_detail_plan.get("rest_amount")),
							"payTime": str(repayment_detail_plan.get('plan_pay_date')),
							"period": per
						}
					)
				else:
					repayment_detail_plan = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("nqh_repayment_normal_settle_projectId"),
						enviroment=self.env,
						period=per,
						repayment_plan_type=plan_pay_type_plan
					)
					param['repaymentPlanList'][y].update(
						{
							"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
							"planPayDate": str(repayment_detail_plan.get('plan_pay_date')),
							"curAmount": float(repayment_detail_plan.get("rest_amount")),
							"payAmount": float(repayment_detail_plan.get("rest_amount")),
							"payTime": str(repayment_detail_plan.get('plan_pay_date')),
							"period": per
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
				enviroment=self.env,
				product="pintic"
			)
			self.assertEqual(rep['resultCode'], data[0]['msgCode'])
			self.assertEqual(rep['content']['message'], "交易成功")
			self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))


if __name__ == '__main__':
	unittest.main()
