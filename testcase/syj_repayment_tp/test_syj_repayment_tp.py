#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2019-05-31 16:21:20
@describe:
"""

import unittest
import os
import json
import time
import sys
import warnings

from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = Logger(logger="test_syj_repayment_tp").getlog()


class SyjRepayment(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = sys.argv[3]
		file = Config().get_item('File', 'syj_repayment_case_file')
		cls.r = Common.conn_redis(cls.env)
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@classmethod
	def tearDownClass(cls):
		pass

	def test_0_approved(self):
		"""随意借进件同意接口"""
		data = excel_table_byname(self.excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		Common.p2p_get_userinfo("syj_repayment", self.env)
		self.r.mset(
			{
				"syj_repayment_sourceProjectId": Common.get_random("sourceProjectId"),
				"syj_repayment_sourceUserId": Common.get_random("userid"),
				"syj_repayment_transactionId": "Apollo" + Common.get_random("transactionId")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("syj_repayment_sourceProjectId"),
				"sourceUserId": self.r.get("syj_repayment_sourceUserId"),
				"transactionId": self.r.get("syj_repayment_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": self.r.get("syj_repayment_cardNum"),
				"custName": self.r.get("syj_repayment_custName"),
				"phone": self.r.get("syj_repayment_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": self.r.get("syj_repayment_phone")})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.r.set("syj_repayment_projectId", json.loads(rep.text)['content']['projectId'])
		self.assertEqual(int(data[0]['msgCode']), json.loads(rep.text)['resultCode'])
		self.assertEqual("交易成功", json.loads(rep.text)['content']['message'], "进件失败")
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('syj_repayment_projectId'),
			enviroment=self.env
		)

	def test_1_loan(self):
		"""随意借放款接口"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'loan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("syj_repayment_sourceProjectId"),
				"sourceUserId": self.r.get("syj_repayment_sourceUserId"),
				"projectId": self.r.get("syj_repayment_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("syj_repayment_cardNum"),
				"bankPhone": self.r.get("syj_repayment_phone")
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['msgCode']), json.loads(rep.text)['resultCode'])
		self.assertEqual("交易成功", json.loads(rep.text)['content']['message'], "放款申请失败")

	def test_2_query_loan_status(self):
		"""随意借放款结果查询接口"""
		time.sleep(8)
		GetSqlData.change_pay_status(self.env, self.r.get("syj_repayment_projectId"))
		GetSqlData.loan_set(self.env, self.r.get("syj_repayment_projectId"))
		data = excel_table_byname(self.excel, 'query_loan_status')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("syj_repayment_sourceProjectId"),
				"sourceUserId": self.r.get("syj_repayment_sourceUserId"),
				"projectId": self.r.get("syj_repayment_projectId"),
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
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
		data = excel_table_byname(self.excel, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['asset'].update(
			{
				"projectId": self.r.get("syj_repayment_projectId"),
				"sourceProjectId": self.r.get("syj_repayment_sourceProjectId"),
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(int(data[0]['msgCode']), json.loads(rep.text)['resultCode'])
		self.assertEqual("交易成功", json.loads(rep.text)['content']['message'], "资产同步失败")

	def test_4_repayment_one_period(self):
		"""随意借还款一期"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['repayment'].update(
			{
				"projectId": self.r.get("syj_repayment_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2"
		}
		for i in param['repaymentDetailList']:
			if i['repaymentPlanType'] in ("1", "2"):
				plan_pay_type = plan_type.get(i['repaymentPlanType'])
				repayment_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("syj_repayment_projectId"),
					enviroment=self.env,
					period=i['period'],
					repayment_plan_type=plan_pay_type
				)
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
						"planPayDate": Common.get_time("-"),
						"payTime": Common.get_time("-")
					}
				)
		for y in param['repaymentPlanList']:
			plan_pay_type_plan = plan_type.get(y['repaymentPlanType'])
			repayment_detail_plan = GetSqlData.get_repayment_detail(
				project_id=self.r.get("syj_repayment_projectId"),
				enviroment=self.env,
				period=y['period'],
				repayment_plan_type=plan_pay_type_plan
			)
			y.update(
				{
					"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
					"planPayDate": Common.get_time("-"),
					"curAmount": float(repayment_detail_plan.get("rest_amount")),
					"payAmount": float(repayment_detail_plan.get("rest_amount")),
					"payTime": Common.get_time("-")
				}
			)
		for i in param['feePlanList']:
			i.update(
				{
					"sourcePlanId": Common.get_random("serviceSn"),
					"planPayDate": Common.get_time("-")
				}
			)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])
		self.assertEqual(json.loads(rep.text)['content']['message'], "交易成功")


if __name__ == '__main__':
	unittest.main()
