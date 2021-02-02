#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth: buxiangjie
@date:
@describe: 橙分期12期退货
"""
import unittest
import os
import json
import time
import sys

from common.common_func import Common
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Cfq12PeriodsTp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = "qa"
		cls.sql = GetSqlData()
		cls.r = Common.conn_redis(environment=cls.env)
		cls.file = Config().get_item('File', 'cfq_12_periods_return_case_file')

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_approved(self):
		"""橙分期进件同意接口"""
		data = excel_table_byname(self.file, 'approved')
		param = json.loads(data[0]['param'])
		Common.p2p_get_userinfo("cfq_12_periods_return", self.env)
		self.r.mset(
			{
				"cfq_12_periods_return_sourceProjectId": Common.get_random("sourceProjectId"),
				"cfq_12_periods_return_sourceUserId": Common.get_random("userid"),
				"cfq_12_periods_return_transactionId": "Apollo" + Common.get_random("transactionId"),
				"cfq_12_periods_return_phone": Common.get_random("phone")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("cfq_12_periods_return_sourceProjectId"),
				"sourceUserId": self.r.get("cfq_12_periods_return_sourceUserId"),
				"transactionId": self.r.get("cfq_12_periods_return_transactionId")
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time("-"),
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": self.r.get("cfq_12_periods_return_cardNum"),
				"custName": self.r.get("cfq_12_periods_return_custName"),
				"phone": self.r.get("cfq_12_periods_return_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": self.r.get("cfq_12_periods_return_phone")})
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
		self.r.set("cfq_12_periods_return_projectId", rep['content']['projectId'])
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))
		# 修改进件审核状态
		GetSqlData.change_project_audit_status(
			project_id=self.r.get("cfq_12_periods_return_projectId"),
			environment=self.env
		)

	def test_101_query_audit_status(self):
		"""橙分期进件审核结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=self.r.get("cfq_12_periods_return_projectId"),
			environment=self.env
		)
		data = excel_table_byname(self.file, 'query_audit_status')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("cfq_12_periods_return_sourceProjectId"),
				"projectId": self.r.get("cfq_12_periods_return_projectId")
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
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	def test_101_loan_notice(self):
		"""橙分期放款通知接口"""
		data = excel_table_byname(self.file, 'loan_notice')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("cfq_12_periods_return_sourceProjectId"),
				"sourceUserId": self.r.get("cfq_12_periods_return_sourceUserId"),
				"projectId": self.r.get("cfq_12_periods_return_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("cfq_12_periods_return_cardNum"),
				"bankPhone": self.r.get("cfq_12_periods_return_phone"),
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
			environment=self.env,
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], int(data[0]['msgCode']))

	def test_102_loanasset(self):
		"""橙分期进件放款同步接口"""
		global period
		data = excel_table_byname(self.file, 'loan_asset')
		param = json.loads(data[0]['param'])
		first_year = str(Common.get_repaydate(12)[0].split(' ')[0].split('-')[0])
		first_day = str(Common.get_repaydate(12)[0].split(' ')[0].split('-')[1])
		last_year = str(Common.get_repaydate(12)[-1].split(' ')[0].split('-')[0])
		last_day = str(Common.get_repaydate(12)[-1].split(' ')[0].split('-')[1])
		param['asset'].update(
			{
				"projectId": self.r.get("cfq_12_periods_return_projectId"),
				"sourceProjectId": self.r.get("cfq_12_periods_return_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": first_year + '-' + first_day + '-' + '10 23:59:59',
				"lastRepaymentDate": last_year + '-' + last_day + '-' + '10 23:59:59',
				"loanTime": Common.get_time("-")
			}
		)

		for i in param['repaymentPlanList']:
			origin_date = Common.get_repaydate(12)
			year = origin_date[i['period'] - 1].split(' ')[0].split('-')[0]
			day = origin_date[i['period'] - 1].split(' ')[0].split('-')[1]
			plan_pay_date = year + '-' + day + '-' + '10 23:59:59'
			i.update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": plan_pay_date
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


if __name__ == '__main__':
	unittest.main()
