#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe:借去花全部结清
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

logger = Logger(logger="test_jqh_repayment_normal_settle_tp").getlog()


class JqhRepaymentNormalSettle(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = "qa"
		file = Config().get_item('File', 'jqh_repayment_normal_settle_case_file')
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file
		cls.r = Common.conn_redis(cls.env)

	@classmethod
	def tearDownClass(cls):
		pass

	def test_0_approved(self):
		"""借去花进件同意接口"""
		data = excel_table_byname(self.excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo("jqh_repayment_normal_settle", self.env)
		param = json.loads(data[0]['param'])
		self.r.mset(
			{
				"jqh_repayment_normal_settle_sourceProjectId": Common.get_random("sourceProjectId"),
				"jqh_repayment_normal_settle_sourceUserId": Common.get_random("userid"),
				"jqh_repayment_normal_settle_transactionId": "Apollo" + Common.get_random("transactionId"),
				"jqh_repayment_normal_settle_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("jqh_repayment_normal_settle_sourceProjectId"),
				"sourceUserId": self.r.get("jqh_repayment_normal_settle_sourceUserId"),
				"transactionId": self.r.get("jqh_repayment_normal_settle_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": self.r.get("jqh_repayment_normal_settle_cardNum"),
				"custName": self.r.get("jqh_repayment_normal_settle_custName"),
				"phone": self.r.get("jqh_repayment_normal_settle_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": self.r.get("jqh_repayment_normal_settle_phone")})
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
		self.r.set("jqh_repayment_normal_settle_projectId", rep['content']['projectId'])
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	def test_1_loan(self):
		"""借去花放款接口"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'loan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("jqh_repayment_normal_settle_sourceProjectId"),
				"sourceUserId": self.r.get("jqh_repayment_normal_settle_sourceUserId"),
				"projectId": self.r.get("jqh_repayment_normal_settle_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("jqh_repayment_normal_settle_cardNum"),
				"bankPhone": self.r.get("jqh_repayment_normal_settle_phone")
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

	def test_2_loanasset(self):
		"""借去花进件放款同步接口"""
		global period
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
				"projectId": self.r.get("jqh_repayment_normal_settle_projectId"),
				"sourceProjectId": self.r.get("jqh_repayment_normal_settle_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": Common.get_repaydate(period)[0],
				"lastRepaymentDate": Common.get_repaydate(period)[-1],
				"loanTime": Common.get_time("-")
			}
		)
		for i in range(0, period * 4):
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

	def test_3_repayment_normal_settle(self):
		"""借去花全部结清"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		for per in range(1, 7):
			amount = GetSqlData.get_repayment_amount(
				environment=self.env,
				project_id=self.r.get("jqh_repayment_normal_settle_projectId"),
				period=per
			)
			param['repayment'].update(
				{
					"projectId": self.r.get("jqh_repayment_normal_settle_projectId"),
					"sourceRepaymentId": Common.get_random("sourceProjectId"),
					"payTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-"),
					"successAmount": amount
				}
			)
			plan_type = {
				"Principal": "1",
				"Interest": "2"
			}
			for i in range(0, len(param['repaymentDetailList'])):
				plan_pay_type = plan_type[param['repaymentDetailList'][i]['repaymentPlanType']]
				plan_catecory = param['repaymentDetailList'][i]['planCategory']
				asset_plan_owner = param['repaymentDetailList'][i]['assetPlanOwner']
				if asset_plan_owner == "foundPartner":
					if plan_catecory == 1 or plan_catecory == 2:
						repayment_detail = GetSqlData.get_repayment_detail(
							project_id=self.r.get("jqh_repayment_normal_settle_projectId"),
							environment=self.env, period=param['repaymentDetailList'][i]['period'],
							repayment_plan_type=plan_pay_type)
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
						param['repaymentDetailList'][i].update(
							{
								"sourceRepaymentDetailId": Common.get_random("serviceSn"),
								"sourceCreateTime": Common.get_time("-"),
								"planPayDate": Common.get_repaydate("6")[0].split(" ")[0],
								"payTime": Common.get_time("-")
							}
						)
				elif asset_plan_owner == "financePartner":
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("jqh_repayment_normal_settle_projectId"),
						environment=self.env, period=param['repaymentDetailList'][i]['period'],
						repayment_plan_type=plan_pay_type)
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
			for i in range(0, len(param['repaymentPlanList'])):
				plan_list_pay_type = plan_type[param['repaymentPlanList'][i]['repaymentPlanType']]
				plan_list_asset_plan_owner = param['repaymentPlanList'][i]['assetPlanOwner']
				if plan_list_asset_plan_owner == 'financePartner':
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("jqh_repayment_normal_settle_projectId"),
						environment=self.env, period=param['repaymentPlanList'][i]['period'],
						repayment_plan_type=plan_list_pay_type)
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
						project_id=self.r.get("jqh_repayment_normal_settle_projectId"),
						environment=self.env, period=param['repaymentPlanList'][i]['period'],
						repayment_plan_type=plan_list_pay_type)
					param['repaymentPlanList'][i].update(
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
				environment=self.env,
				product="pintic"
			)
			self.assertEqual(rep['resultCode'], data[0]['msgCode'])
			self.assertEqual(rep['content']['message'], "交易成功")
			self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))


if __name__ == '__main__':
	unittest.main()
