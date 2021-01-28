#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2019-05-31 16:21:20
@describe:随意借流程
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

logger = Logger(logger="test_syj_tp").getlog()


class SyjTp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = "test"
		cls.file = Config().get_item('File', 'syj_case_file')
		cls.r = Common.conn_redis(cls.env)

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_approved(self):
		"""随意借进件同意接口"""
		data = excel_table_byname(self.file, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('syj', self.env)
		param = json.loads(data[0]['param'])
		self.r.mset(
			{
				"syj_sourceProjectId": Common.get_random("sourceProjectId"),
				"syj_sourceUserId": Common.get_random("userid"),
				"syj_transactionId": "Apollo" + Common.get_random("transactionId")
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get("syj_sourceProjectId"),
				"sourceUserId": self.r.get("syj_sourceUserId"),
				"transactionId": self.r.get("syj_transactionId")
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": self.r.get("syj_cardNum"),
				"custName": self.r.get("syj_custName"),
				"phone": Common.get_random("phone")
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
		self.r.set("syj_projectId", rep['content']['projectId'])
		self.assertEqual(int(data[0]['msgCode']), rep['resultCode'])
		self.assertEqual("交易成功", rep['content']['message'], "进件失败")
		GetSqlData.change_project_audit_status(
			project_id=self.r.get("syj_projectId"),
			environment=self.env
		)

	def test_101_loan(self):
		"""随意借放款接口"""
		data = excel_table_byname(self.file, 'loan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("syj_sourceProjectId"),
				"sourceUserId": self.r.get("syj_sourceUserId"),
				"projectId": self.r.get("syj_projectId"),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("syj_cardNum"),
				"bankPhone": self.r.get("syj_phone")
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
		self.assertEqual(int(data[0]['msgCode']), rep['resultCode'])
		self.assertEqual("交易成功", rep['content']['message'], "放款申请失败")
		GetSqlData.change_pay_status(
			project_id=self.r.get("syj_projectId"),
			environment=self.env
		)

	def test_102_query_loan_status(self):
		"""随意借放款结果查询接口"""
		time.sleep(5)
		GetSqlData.change_pay_status(
			project_id=self.r.get("syj_projectId"),
			environment=self.env
		)
		GetSqlData.loan_set(self.env, self.r.get("syj_projectId"))
		data = excel_table_byname(self.file, 'query_loan_status')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get("syj_sourceProjectId"),
				"sourceUserId": self.r.get("syj_sourceUserId"),
				"projectId": self.r.get("syj_projectId"),
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
		self.assertEqual(int(data[0]['msgCode']), rep['resultCode'])
		self.assertEqual("SUCCESS", rep['content']['loanStatus'], "放款失败")

	def test_103_loanasset(self):
		"""随意借进件放款同步接口"""
		data = excel_table_byname(self.file, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['asset'].update(
			{
				"projectId": self.r.get("syj_projectId"),
				"sourceProjectId": self.r.get("syj_sourceProjectId"),
				"transactionId": "Apollo" + Common.get_random("transactionId"),
				"repaymentDay": Common.get_time("day").split('-')[1],
				"firstRepaymentDate": Common.get_repaydate(6)[0],
				"lastRepaymentDate": Common.get_repaydate(6)[-1],
				"loanTime": Common.get_time("-")
			}
		)
		for i in range(len(param['repaymentPlanList'])):
			param['repaymentPlanList'][i].update(
				{
					"sourcePlanId": Common.get_random("sourceProjectId"),
					"planPayDate": Common.get_repaydate(6)[param['repaymentPlanList'][i]['period'] - 1]
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
		self.assertEqual(int(data[0]['msgCode']), rep['resultCode'])
		self.assertEqual("交易成功", rep['content']['message'], "资产同步失败")

	# @unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] == "compensation", "-")
	def test_3_compensation(self):
		"""随意借代偿一期"""
		data = excel_table_byname(self.file, 'compensation')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": self.r.get("syj_projectId"),
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": self.r.get("syj_sourceProjectId"),
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
					project_id=self.r.get("syj_projectId"),
					environment=self.env,
					period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType'])
				)
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("syj_projectId"),
					environment=self.env,
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
			environment=self.env,
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])

	@unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] == "after_comp_repay", "-")
	def test_4_after_comp_repay(self):
		"""随意借代偿后还款"""
		global period, plan_pay_type, plan_list_detail
		data = excel_table_byname(self.file, 'after_comp_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": self.r.get("syj_projectId"),
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
		for i in param['repaymentDetailList']:
			plan_pay_type = plan_type[i['repaymentPlanType']]
			plan_catecory = i['planCategory']
			asset_plan_owner = i['assetPlanOwner']
			if asset_plan_owner == "foundPartner":
				if plan_catecory == 1 or plan_catecory == 2:
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get("syj_projectId"),
						environment=self.env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(repayment_detail.get('plan_pay_date')),
							"curAmount": float(repayment_detail.get('cur_amount')),
							"restAmount": float(repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
				else:
					plan_list_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("syj_projectId"),
						environment=self.env,
						period=period,
						repayment_plan_type=3,
						feecategory=i['planCategory']
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(plan_list_detail.get("plan_pay_date")),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			elif asset_plan_owner == "financePartner":
				if plan_catecory == 1 or plan_catecory == 2:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get("syj_projectId"),
						environment=self.env,
						period=period,
						repayment_plan_type=plan_pay_type
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(user_repayment_detail.get('plan_pay_date')),
							"curAmount": float(user_repayment_detail.get('cur_amount')),
							"restAmount": float(user_repayment_detail.get('rest_amount')),
							"payTime": Common.get_time("-"),
							"period": period
						}
					)
			else:
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("syj_projectId"),
					environment=self.env,
					period=period,
					repayment_plan_type=3,
					feecategory=i['planCategory']
				)
				i.update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": Common.get_time("-"),
						"planPayDate": str(plan_list_detail.get("plan_pay_date")),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in param['repaymentPlanList']:
			plan_list_pay_type = plan_type[i['repaymentPlanType']]
			plan_list_asset_plan_owner = i['assetPlanOwner']
			if plan_list_asset_plan_owner == 'financePartner':
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get("syj_projectId"),
					environment=self.env,
					period=period,
					repayment_plan_type=plan_list_pay_type
				)
				i.update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail.get('cur_amount')),
						"restAmount": float(plan_list_detail.get('rest_amount')),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
			elif plan_list_asset_plan_owner == 'foundPartner':
				plan_list_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("syj_projectId"),
					environment=self.env,
					period=i['period'],
					repayment_plan_type=plan_list_pay_type
				)
				i.update(
					{
						"sourcePlanId": plan_list_detail.get('source_plan_id'),
						"planPayDate": Common.get_time("-"),
						"curAmount": float(plan_list_detail.get('cur_amount')),
						"restAmount": float(plan_list_detail.get('rest_amount')),
						"payTime": Common.get_time("-"),
						"period": period
					}
				)
		for i in param['feePlanList']:
			plan_list_detail = GetSqlData.get_user_repayment_detail(
				project_id=self.r.get("syj_projectId"),
				environment=self.env,
				period=i['period'],
				repayment_plan_type=3,
				feecategory=i['feeCategory']
			)
			i.update(
				{
					"sourcePlanId": plan_list_detail.get('source_plan_id'),
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
			data=json.dumps(param, ensure_ascii=False),
			environment=self.env,
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])
		self.assertEqual(rep['content']['message'], "交易成功")


if __name__ == '__main__':
	unittest.main()
