#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2019-05-31 16:21:20
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

logger = Logger(logger="test_syj_repayment_advance_tp").getlog()


class SyjRepaymentAdvance(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = sys.argv[3]
		cls.r = Common.conn_redis(cls.env)
		cls.file = Config().get_item('File', 'syj_repayment_advance_case_file')

	@classmethod
	def tearDownClass(cls):
		pass

	def test_0_approved(self):
		"""随意借进件同意接口"""
		data = excel_table_byname(self.file, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('syj_repayment_advance', self.env)
		param = json.loads(data[0]['param'])
		self.r.mset(
			{
				"syj_repayment_advance_sourceProjectId": Common.get_random("sourceProjectId"),
				"syj_repayment_advance_sourceUserId": Common.get_random("userid"),
				"syj_repayment_advance_transactionId": "Apollo" + Common.get_random("transactionId"),
				"syj_repayment_advance_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("syj_repayment_advance_sourceProjectId"),
				"sourceUserId": self.r.get("syj_repayment_advance_sourceUserId"),
				"transactionId": self.r.get("syj_repayment_advance_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": self.r.get("syj_repayment_advance_cardNum"),
				"custName": self.r.get("syj_repayment_advance_custName"),
				"phone": self.r.get("syj_repayment_advance_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": self.r.get("syj_repayment_advance_phone")})
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.r.set("syj_repayment_advance_projectId", json.loads(rep.text)['content']['projectId'])
		self.assertEqual(int(data[0]['msgCode']), json.loads(rep.text)['resultCode'])
		self.assertEqual("交易成功", json.loads(rep.text)['content']['message'], "进件失败")

	def test_1_loan(self):
		"""随意借放款接口"""
		time.sleep(5)
		data = excel_table_byname(self.file, 'loan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("syj_repayment_advance_sourceProjectId"),
				"sourceUserId": self.r.get("syj_repayment_advance_sourceUserId"),
				"projectId": self.r.get("syj_repayment_advance_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("syj_repayment_advance_cardNum"),
				"bankPhone": self.r.get("syj_repayment_advance_phone")
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['msgCode']), json.loads(rep.text)['resultCode'])
		self.assertEqual("交易成功", json.loads(rep.text)['content']['message'], "放款申请失败")

	def test_2_query_loan_status(self):
		"""随意借放款结果查询接口"""
		GetSqlData.loan_set(self.env, self.r.get("syj_repayment_advance_projectId"))
		data = excel_table_byname(self.file, 'query_loan_status')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("syj_repayment_advance_sourceProjectId"),
				"sourceUserId": self.r.get("syj_repayment_advance_sourceUserId"),
				"projectId": self.r.get("syj_repayment_advance_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn")
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['msgCode']), json.loads(rep.text)['resultCode'])
		self.assertEqual("SUCCESS", json.loads(rep.text)['content']['loanStatus'], "放款失败")

	def test_3_loanasset(self):
		"""随意借进件放款同步接口"""
		global period
		time.sleep(5)
		data = excel_table_byname(self.file, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		if len(param['repaymentPlanList']) / 2 == 1.5:
			period = 3
		elif len(param['repaymentPlanList']) / 2 == 3:
			period = 6
		elif len(param['repaymentPlanList']) / 2 == 4.5:
			period = 9
		elif len(param['repaymentPlanList']) / 2 == 12:
			period = 12
		param['asset'].update(
			{
				"projectId": self.r.get("syj_repayment_advance_projectId"),
				"sourceProjectId": self.r.get("syj_repayment_advance_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": Common.get_repaydate(period)[0],
				"lastRepaymentDate": Common.get_repaydate(period)[-1],
				"loanTime": Common.get_time("-")
			}
		)

		for i in range(period * 2):
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['msgCode']), json.loads(rep.text)['resultCode'])
		self.assertEqual("交易成功", json.loads(rep.text)['content']['message'], "资产同步失败")

	def test_3_repayment_one_period(self):
		"""随意借还款一期"""
		time.sleep(5)
		data = excel_table_byname(self.file, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			environment=self.env,
			project_id=self.r.get("syj_repayment_advance_projectId"),
			period=param['repaymentDetailList'][0]['period']
		)
		param['repayment'].update(
			{
				"projectId": self.r.get("syj_repayment_advance_projectId"),
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
			repayment_detail = GetSqlData.get_repayment_plan_date(
				project_id=self.r.get("syj_repayment_advance_projectId"), environment=self.env,
				repayment_plan_type=plan_pay_type, period=i['period'])
			i.update(
				{
					"sourceRepaymentDetailId": Common.get_random("serviceSn"),
					"sourceCreateTime": Common.get_time("-"),
					"planPayDate": str(repayment_detail.get('plan_pay_date')),
					"thisPayAmount": float(repayment_detail.get('rest_amount')),
					"payTime": Common.get_time("-")
				}
			)
		for y in param['repaymentPlanList']:
			plan_pay_type_plan = plan_type.get(y['repaymentPlanType'])
			repayment_detail_plan = GetSqlData.get_repayment_plan_date(
				project_id=self.r.get("syj_repayment_advance_projectId"), environment=self.env,
				repayment_plan_type=plan_pay_type_plan, period=y['period'])
			y.update(
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
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])
		self.assertEqual(json.loads(rep.text)['content']['message'], "交易成功")


if __name__ == '__main__':
	unittest.main()
