#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2020-03-30 10:38:20
@describe:随意借V2流程
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

logger = Logger(logger="test_syjv2_tp").getlog()


class Syjv2Tp(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.env = "qa"
		cls.r = Common.conn_redis(enviroment=cls.env)
		file = Config().get_item('File', 'syjv2_case_file')
		cls.excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@classmethod
	def tearDownClass(cls):
		pass

	def test_100_approved(self):
		"""随意借V2进件同意接口"""
		data = excel_table_byname(self.excel, 'approved')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('syjv2', self.env)
		param = json.loads(data[0]['param'])
		self.r.mset(
			{
				"syjv2_sourceUserId": Common.get_random('userid'),
				"syjv2_transactionId": Common.get_random('transactionId'),
				"syjv2_phone": Common.get_random('phone'),
				"syjv2_sourceProjectId": Common.get_random('sourceProjectId')
			}
		)
		param.update(
			{
				"sourceProjectId": self.r.get('syjv2_sourceProjectId'),
				"sourceUserId": self.r.get('syjv2_sourceUserId'),
				"transactionId": self.r.get('syjv2_transactionId')
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
		param['personalInfo'].update(
			{
				"cardNum": self.r.get('syjv2_cardNum'),
				"custName": self.r.get('syjv2_custName'),
				"phone": self.r.get('syjv2_phone')
			}
		)
		param['cardInfo'].update({"bankPhone": self.r.get('syjv2_phone')})
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
		self.r.set('syjv2_projectId', rep['content']['projectId'])
		self.assertEqual(int(data[0]['msgCode']), rep['resultCode'])
		self.assertEqual("交易成功", rep['content']['message'], "进件失败")
		GetSqlData.change_project_audit_status(
			project_id=self.r.get('syjv2_projectId'),
			enviroment=self.env
		)
		GetSqlData.project_audit_status(
			project_id=self.r.get('syjv2_projectId'),
			enviroment=self.env
		)

	def test_101_loan(self):
		"""随意借V2放款接口"""
		time.sleep(5)
		data = excel_table_byname(self.excel, 'loan')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('syjv2_sourceProjectId'),
				"sourceUserId": self.r.get('syjv2_sourceUserId'),
				"projectId": self.r.get('syjv2_projectId'),
				"serviceSn": "SaasL-" + Common.get_random("serviceSn"),
				"id": self.r.get("syjv2_cardNum"),
				"bankPhone": self.r.get("syjv2_phone")
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
		self.assertEqual(int(data[0]['msgCode']), rep['resultCode'])
		self.assertEqual("交易成功", rep['content']['message'], "放款申请失败")


	def test_102_query_loan_status(self):
		"""随意借V2放款结果查询接口"""
		data = excel_table_byname(self.excel, 'query_loan_status')
		print("接口名称:%s" % data[0]['casename'])
		GetSqlData.change_pay_status(
			project_id=self.r.get('syjv2_projectId'),
			enviroment=self.env
		)
		GetSqlData.loan_set(self.env, self.r.get('syjv2_projectId'))
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": self.r.get('syjv2_sourceProjectId'),
				"sourceUserId": self.r.get('syjv2_sourceUserId'),
				"projectId": self.r.get('syjv2_projectId'),
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
			enviroment=self.env,
			product="pintic"
		)
		self.assertEqual(int(data[0]['msgCode']), rep['resultCode'])
		self.assertEqual("SUCCESS", rep['content']['loanStatus'], "放款失败")

	def test_103_loanasset(self):
		"""随意借V2进件放款同步接口"""
		data = excel_table_byname(self.excel, 'loan_asset')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['asset'].update(
			{
				"projectId": self.r.get('syjv2_projectId'),
				"sourceProjectId": self.r.get('syjv2_sourceProjectId'),
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
			enviroment=self.env,
			product="pintic"
		)
		self.assertEqual(int(data[0]['msgCode']), rep['resultCode'])
		self.assertEqual("交易成功", rep['content']['message'], "资产同步失败")

	# @unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] == 'repayment', "条件成立时执行")
	def test_104_repayment_one_period(self):
		"""随意借V2还款一期"""
		data = excel_table_byname(self.excel, 'repayment')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['repayment'].update(
			{
				"projectId": self.r.get("syjv2_projectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"payTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		plan_type = {
			"Principal": "1",
			"Interest": "2"
		}
		for i in range(len(param['repaymentDetailList'])):
			if param['repaymentDetailList'][i]['repaymentPlanType'] in ("1", "2"):
				plan_pay_type = plan_type.get(param['repaymentDetailList'][i]['repaymentPlanType'])
				repayment_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("syjv2_projectId"),
					enviroment=self.env,
					period=param['repaymentDetailList'][i]['period'],
					repayment_plan_type=plan_pay_type)
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": Common.get_time("-"),
						"planPayDate": str(repayment_detail.get('plan_pay_date')),
						"payTime": Common.get_time("-")
					}
				)
			else:
				repayment_detail = GetSqlData.get_repayment_detail(
					project_id=self.r.get("syjv2_projectId"),
					enviroment=self.env,
					period=param['repaymentDetailList'][i]['period'],
					repayment_plan_type=1)
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"sourceCreateTime": Common.get_time("-"),
						"planPayDate": str(repayment_detail.get('plan_pay_date')),
						"payTime": Common.get_time("-")
					}
				)
		for y in range(len(param['repaymentPlanList'])):
			plan_pay_type_plan = plan_type.get(param['repaymentPlanList'][y]['repaymentPlanType'])
			repayment_detail_plan = GetSqlData.get_repayment_detail(
				project_id=self.r.get("syjv2_projectId"),
				enviroment=self.env,
				period=param['repaymentPlanList'][y]['period'],
				repayment_plan_type=plan_pay_type_plan)
			param['repaymentPlanList'][y].update(
				{
					"sourcePlanId": repayment_detail_plan.get('source_plan_id'),
					"planPayDate": str(repayment_detail_plan.get('plan_pay_date')),
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
		param['reliefApply'].update(
			{
				"projectId": self.r.get("syjv2_projectId"),
				"reliefTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-"),
				"sourceReliefApplyId": Common.get_random("serviceSn")
			}
		)
		for i in param['reliefDetailList']:
			i.update(
				{
					"planPayDate": param['feePlanList'][0]['planPayDate'],
					"reliefTime": Common.get_time("-"),
					"sourceCreateTime": Common.get_time("-"),
					"sourcePlanId": Common.get_random("serviceSn"),
					"sourceReliefDetailId": Common.get_random("serviceSn")
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

	# @unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] in ('compensation', 'after_comp_repay'), "条件成立时执行")
	def test_106_compensation(self):
		"""随意借V2代偿一期"""
		data = excel_table_byname(self.excel, 'compensation')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param['assetSwapInfo'].update(
			{
				"projectId": self.r.get('syjv2_projectId'),
				"sourceApplyId": Common.get_random("serviceSn"),
				"actionTime": Common.get_time("-"),
				"sourceCreateTime": Common.get_time("-")
			}
		)
		for i in param['assetSwapDetailList']:
			i.update(
				{
					"projectId": self.r.get('syjv2_sourceProjectId'),
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
					project_id=self.r.get('syjv2_projectId'),
					enviroment=self.env,
					period=i['period'],
					repayment_plan_type=plan_pay_type.get(i['repaymentPlanType'])
				)
			elif i['assetPlanOwner'] == "financePartner":
				plan_list_detail = GetSqlData.get_user_repayment_detail(
					project_id=self.r.get('syjv2_projectId'),
					enviroment=self.env,
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
			enviroment=self.env,
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])

	# @unittest.skip("-")
	# @unittest.skipUnless(sys.argv[4] == 'after_comp_repay', "条件成立时执行")
	def test_107_after_comp_repay(self):
		"""随意借V2代偿后还款"""
		global period, plan_pay_type, plan_list_detail
		data = excel_table_byname(self.excel, 'after_comp_repay')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		period = 1
		param['repayment'].update(
			{
				"projectId": self.r.get('syjv2_projectId'),
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
						project_id=self.r.get('syjv2_projectId'),
						enviroment=self.env,
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
						project_id=self.r.get('syjv2_projectId'),
						enviroment=self.env,
						period=period,
						repayment_plan_type=3,
						feecategory=i['planCategory']
					)
					repayment_detail = GetSqlData.get_repayment_detail(
						project_id=self.r.get('syjv2_projectId'),
						enviroment=self.env,
						period=1,
						repayment_plan_type=2
					)
					i.update(
						{
							"sourceRepaymentDetailId": Common.get_random("serviceSn"),
							"sourceCreateTime": Common.get_time("-"),
							"planPayDate": str(plan_list_detail.get("plan_pay_date")),
							"payTime": str(repayment_detail.get("plan_pay_date")),
							"period": period
						}
					)
			elif asset_plan_owner == "financePartner":
				if plan_catecory == 1 or plan_catecory == 2:
					user_repayment_detail = GetSqlData.get_user_repayment_detail(
						project_id=self.r.get('syjv2_projectId'),
						enviroment=self.env,
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
					project_id=self.r.get('syjv2_projectId'),
					enviroment=self.env,
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
					project_id=self.r.get('syjv2_projectId'),
					enviroment=self.env,
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
					project_id=self.r.get('syjv2_projectId'),
					enviroment=self.env,
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
				project_id=self.r.get("syjv2_projectId"),
				enviroment=self.env,
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
			enviroment=self.env,
			product="pintic"
		)
		self.assertEqual(rep['resultCode'], data[0]['msgCode'])
		self.assertEqual(rep['content']['message'], "交易成功")


if __name__ == '__main__':
	unittest.main()
