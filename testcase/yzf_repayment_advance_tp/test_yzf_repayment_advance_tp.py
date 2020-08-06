#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:
@describe: 翼支付提前结清
"""
import unittest
import warnings
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

logger = Logger(logger="test_yzf_repayment_advance_tp").getlog()


class YzfRepaymentAdvance(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = sys.argv[3]
		file = Config().get_item('File', 'yzf_repayment_advance_case_file')
		cls.r = Common.conn_redis(cls.env)
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@classmethod
	def tearDownClass(cls):
		pass

	def test_0_approved(self):
		"""翼支付进件同意接口"""
		data = excel_table_byname(self.excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('yzf_repayment_advance', self.env)
		param = json.loads(data[0]['param'])
		self.r.mset(
			{
				"yzf_repayment_advance_sourceProjectId": Common.get_random("sourceProjectId"),
				"yzf_repayment_advance_sourceUserId": Common.get_random("userid"),
				"yzf_repayment_advance_transactionId": "Apollo" + Common.get_random("transactionId")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("yzf_repayment_advance_sourceProjectId"),
				"sourceUserId": self.r.get("yzf_repayment_advance_sourceUserId"),
				"transactionId": self.r.get("yzf_repayment_advance_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": self.r.get("yzf_repayment_advance_cardNum"),
				"custName": self.r.get("yzf_repayment_advance_custName"),
				"phone": self.r.get("yzf_repayment_advance_phone")
			}
		)
		param['cardInfo'].update({"bankPhone": self.r.get("yzf_repayment_advance_phone")})
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
		self.r.set("yzf_repayment_advance_projectId", json.loads(rep.text)['content']['projectId'])
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))
		GetSqlData.change_project_audit_status(self.r['yzf_repayment_advance_projectId'], self.env)

	def test_1_loan_notice(self):
		"""翼支付放款通知接口"""
		data = excel_table_byname(self.excel, 'loan_notice')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		self.r["yzf_repayment_advance_loan_time"] = Common.get_time("-")
		param.update(
			{
				"sourceProjectId": self.r.get("yzf_repayment_advance_sourceProjectId"),
				"sourceUserId": self.r.get("yzf_repayment_advance_sourceUserId"),
				"projectId": self.r.get("yzf_repayment_advance_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("yzf_repayment_advance_cardNum"),
				"bankPhone": self.r.get("yzf_repayment_advance_phone"),
				"loanTime": self.r.get("yzf_repayment_advance_loan_time")
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("返回信息:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))

	def test_2_loanasset(self):
		"""翼支付进件放款同步接口"""
		global period
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
				"projectId": self.r.get("yzf_repayment_advance_projectId"),
				"sourceProjectId": self.r.get("yzf_repayment_advance_sourceProjectId"),
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))

	def test_3_repayment_settle_in_advance(self):
		"""翼支付提前结清"""
		data = excel_table_byname(self.excel, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = Common().get_json_data('data', 'yzf_settle_in_advance.json')
		param['repayment'].update(
			{
				"projectId": self.r.get("yzf_repayment_advance_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
				"successAmount": 103.36
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2"
		}
		for i in param['repaymentDetailList']:
			i.update(
				{
					"sourceRepaymentDetailId": Common.get_random("transactionId"),
					"relatedPlanId": Common.get_random("sourceProjectId"),
					"payTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-")
				}
			)
			if i['repaymentPlanType'] == 'Principal':
				this_pay_amount = GetSqlData.get_all_repayment_amount(
					enviroment=self.env,
					project_id=self.r.get("yzf_repayment_advance_projectId")
				)
				i.update(
					{
						"thisPayAmount": this_pay_amount
					}
				)
		for i in param['repaymentPlanList']:
			i.update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"payTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-")
				}
			)
			if i['repaymentStatus'] == 'repayment_done':
				i.update(
					{
						"curAmount": GetSqlData.get_all_repayment_amount(
							enviroment=self.env,
							project_id=self.r.get("yzf_repayment_advance_projectId")
						),
						"payAmount": GetSqlData.get_all_repayment_amount(
							enviroment=self.env,
							project_id=self.r.get("yzf_repayment_advance_projectId")
						)
					}
				)
			else:
				if i['assetPlanOwner'] == 'financePartner':
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("yzf_repayment_advance_projectId"),
						enviroment=self.env, period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']]
					)
					i.update(
						{
							"sourcePlanId": plan_list_detail.get('source_plan_id'),
							"planPayDate": str(plan_list_detail.get("plan_pay_date")),
							"curAmount": float(plan_list_detail.get("rest_amount")),
							"payAmount": float(plan_list_detail.get("rest_amount")),
						}
					)
				elif i['assetPlanOwner'] == 'foundPartner':
					plan_list_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("yzf_repayment_advance_projectId"),
						enviroment=self.env, period=i['period'],
						repayment_plan_type=plan_type[i['repaymentPlanType']]
					)
					i.update(
						{
							"sourcePlanId": plan_list_detail.get('source_plan_id'),
							"planPayDate": str(plan_list_detail.get("plan_pay_date")),
							"curAmount": float(plan_list_detail.get("rest_amount")),
							"payAmount": float(plan_list_detail.get("rest_amount")),
						}
					)
		for i in param['feePlanList']:
			i.update(
				{
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
			data=json.dumps(param, ensure_ascii=False).encode('utf-8'),
			enviroment=self.env,
			product="pintic"
		)
		print("响应信息:%s" % rep)
		print("返回json:%s" % rep.text)
		logger.info("返回信息:%s" % rep.text)
		self.assertEqual(json.loads(rep.text)['resultCode'], data[0]['msgCode'])
		self.assertEqual(json.loads(rep.text)['content']['message'], "交易成功")
		self.assertEqual(json.loads(rep.text)['resultCode'], int(data[0]['msgCode']))


if __name__ == '__main__':
	unittest.main()
