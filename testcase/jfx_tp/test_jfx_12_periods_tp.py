# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date: 2019-08-20
@describe:金服侠-牙医贷一期12期产品流程用例
"""

import unittest
import os
import json
import sys
import allure
import pytest

from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = Logger(logger="test_jfx_12_periods_tp").getlog()

@allure.feature("金服侠12期")
class TestJfx12PeriodTp:
	file = Config().get_item('File', 'jfx_mul_case_file')
	excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file

	@allure.title("申请授信")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_100_credit_apply(self, r, env):
		"""额度授信"""
		data = excel_table_byname(self.excel, 'credit_apply_data')
		print("接口名称:%s" % data[0]['casename'])
		Common.p2p_get_userinfo('jfx_12_periods', env)
		r.mset(
			{
				"jfx_12_periods_sourceUserId": Common.get_random('userid'),
				'jfx_12_periods_transactionId': Common.get_random('transactionId'),
				"jfx_12_periods_phone": Common.get_random('phone'),
				"jfx_12_periods_firstCreditDate": Common.get_time()
			}
		)
		param = json.loads(data[0]['param'])
		param['personalInfo'].update(
			{
				"cardNum": r.get('jfx_12_periods_cardNum'),
				"custName": r.get('jfx_12_periods_custName'),
				"phone": r.get('jfx_12_periods_phone'),
				"isDoctor": 1,
				"applicantClinicRelationship": 1
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time()})
		param.update(
			{
				"sourceUserId": r.get('jfx_12_periods_sourceUserId'),
				"serviceSn": Common.get_random('serviceSn'),
				"transactionId": r.get('jfx_12_periods_transactionId')
			}
		)
		# del param["imageInfo"]["businessLicense"] #营业执照
		# del param["imageInfo"]["medicalPracticeCertificate"]  # 本人医师执业证书
		# del param["imageInfo"]["medicalInstitutionLicense"]  # 医疗机构执业许可证
		# del param["imageInfo"]["shareholderCertificate"]  # 股东证明
		# del param["imageInfo"]["authorizationCertificate"]  # 授权证明
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=env
		)
		r.mset(
			{
				"jfx_12_periods_creditId": rep['content']['creditId'],
				"jfx_12_periods_userId": rep['content']['userId']
			}
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("授信结果查询")
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_101_query_result(self, r, env):
		"""授信结果查询"""
		GetSqlData.credit_set(
			enviroment=env,
			credit_id=r.get("jfx_12_periods_creditId")
		)
		data = excel_table_byname(self.excel, 'credit_query_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update({"creditId": r.get('jfx_12_periods_creditId')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("用户额度查询")
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_102_query_user_amount(self, r, env):
		"""用户额度查询"""
		data = excel_table_byname(self.excel, 'query_user_amount')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get('jfx_12_periods_sourceUserId'),
				"userId": r.get('jfx_12_periods_userId')
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
			product="cloudloan",
			enviroment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("上传授信协议")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_103_sign_credit(self, r, env):
		"""上传授信协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'jfx_credit_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('jfx_12_periods_sourceUserId'),
				"contractType": 1,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get('jfx_12_periods_transactionId'),
				"associationId": r.get('jfx_12_periods_creditId')
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
			product="cloudloan",
			enviroment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("进件申请")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_104_project_apply(self, r, env):
		"""进件"""
		data = excel_table_byname(self.excel, 'test_project')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		r.set('jfx_12_periods_sourceProjectId', Common.get_random('sourceProjectId'))
		param.update(
			{
				"sourceProjectId": r.get('jfx_12_periods_sourceProjectId'),
				"sourceUserId": r.get('jfx_12_periods_sourceUserId'),
				"transactionId": r.get('jfx_12_periods_transactionId')
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": r.get('jfx_12_periods_cardNum'),
				"custName": r.get('jfx_12_periods_custName'),
				"phone": r.get('jfx_12_periods_phone')
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time(),
				"applyAmount": 84920.00,
				"applyTerm": 12
			}
		)
		param['loanInfo'].update(
			{
				"loanAmount": 84920.00,
				"assetInterestRate": 0.158156,
				"userInterestRate": 0.158156,
				"loanTerm": 12
			}
		)
		param['cardInfo'].update(
			{
				"bankNameSub": "招商银行",
				"bankCode": "86",
				"bankCardNo": "6214830173648711",
				"unifiedSocialCreditCode": Common.get_random("businessLicenseNo")
			}
		)
		r.set("jfx_12_periods_corporateAccountName", param['cardInfo']['corporateAccountName'])
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=env
		)
		r.set('jfx_12_periods_projectId', rep['content']['projectId'])
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("进件结果查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_105_query_apply_result(self, r, env):
		"""进件结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=r.get('jfx_12_periods_projectId'),
			enviroment=env
		)
		data = excel_table_byname(self.excel, 'project_query_apply_result')
		print("接口名称:%s" % data[0]['casename'])
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get('jfx_12_periods_sourceProjectId'),
				"projectId": r.get('jfx_12_periods_projectId')
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
			product="cloudloan",
			enviroment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("上传借款授信协议")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_106_sign_credit(self, r, env):
		"""上传借款授信协议"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'jfx_credit_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('jfx_12_periods_sourceUserId'),
				"contractType": 5,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get('jfx_12_periods_transactionId'),
				"associationId": r.get('jfx_12_periods_projectId')
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
			product="cloudloan",
			enviroment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("上传借款合同")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_107_contract_sign(self, r, env):
		"""上传借款合同"""
		data = excel_table_byname(self.excel, 'contract_sign')
		print("接口名称:%s" % data[0]['casename'])
		param = Common.get_json_data('data', 'jfx_borrow_periods_contract_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('jfx_12_periods_sourceUserId'),
				"contractType": 2,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get('jfx_12_periods_transactionId'),
				"associationId": r.get('jfx_12_periods_projectId')
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
			product="cloudloan",
			enviroment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("放款申请")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_108_pfa(self, r, env):
		"""放款申请"""
		data = excel_table_byname(self.excel, 'project_loan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get('jfx_12_periods_sourceProjectId'),
				"projectId": r.get('jfx_12_periods_projectId'),
				"sourceUserId": r.get('jfx_12_periods_sourceUserId'),
				"serviceSn": Common.get_random('serviceSn'),
				"accountName": r.get("jfx_12_periods_corporateAccountName"),
				"bankCode": 86,
				"amount": 84920.00,
				"accountNo": "6214830173648711"  # 6227002432220410613
			}
		)
		r.set("jfx_12_periods_pfa_serviceSn", param['serviceSn'])
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']
		GetSqlData.change_pay_status(
			enviroment=env,
			project_id=r.get('jfx_12_periods_projectId')
		)

	@allure.title("放款结果查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_109_pfa_query(self, r, env):
		"""放款结果查询"""
		GetSqlData.loan_set(
			enviroment=env,
			project_id=r.get('jfx_12_periods_projectId')
		)
		data = excel_table_byname(self.excel, 'pfa_query')
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": r.get('jfx_12_periods_pfa_serviceSn')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			enviroment=env,
			product="cloudloan"
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("还款计划查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_110_query_repaymentplan(self, r, env):
		"""还款计划查询"""
		data = excel_table_byname(self.excel, 'repayment_plan')
		param = json.loads(data[0]['param'])
		param.update({"projectId": r.get('jfx_12_periods_projectId')})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			enviroment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']
		r.set("jfx_12_periods_repayment_plan", json.dumps(rep['content']['repaymentPlanList']))

	# # @unittest.skipUnless(sys.argv[4] == "repayment", "条件成立时执行")
	# @unittest.skip("1")
	@allure.title("还款流水推送")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_112_repayment(self, r, env):
		"""还款流水推送"""
		data = excel_table_byname(self.excel, 'repayment')
		param = json.loads(data[0]['param'])
		repayment_plan_list = r.get("jfx_12_periods_repayment_plan")
		success_amount = 0.00
		repayment_detail_list = []
		period = 1
		for i in json.loads(repayment_plan_list):
			if i['period'] == 1:
				plan_detail = {
					"sourceRepaymentDetailId": Common.get_random("transactionId"),
					"payAmount": i['restAmount'],
					"planCategory": i['repaymentPlanType']
				}
				success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
				repayment_detail_list.append(plan_detail)
		param.update(
			{
				"sourceRequestId": Common.get_random("requestNum"),
				"projectId": r.get("jfx_12_periods_projectId"),
				"sourceProjectId": r.get("jfx_12_periods_sourceProjectId"),
				"sourceUserId": r.get("jfx_12_periods_sourceUserId"),
				"serviceSn": Common.get_random("serviceSn"),
				"payTime": Common.get_time("-"),
				"successAmount": success_amount,
				"period": period
			}
		)
		param['repaymentDetailList'] = repayment_detail_list
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			enviroment=env,
			product="cloudloan"
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])

	# @unittest.skip("1")
	# # @unittest.skipUnless(sys.argv[4] == "early_repayment", "满足条件执行")
	@allure.title("提前全部结清")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_113_repayment(self, r, env):
		"""还款流水推送:提前全部结清"""
		data = excel_table_byname(self.excel, 'repayment')
		param = json.loads(data[0]['param'])
		for per in range(1, 13):
			success_amount = GetSqlData.get_repayment_amount(
				project_id=r.get("jfx_12_periods_projectId"), enviroment=env,
				period=per)
			param.update(
				{
					"projectId": r.get('jfx_12_periods_projectId'),
					"transactionId": r.get('jfx_12_periods_transactionId'),
					"sourceProjectId": r.get('jfx_12_periods_sourceProjectId'),
					"sourcePlanId": Common.get_random('sourceProjectId'),
					"sourceRepaymentId": Common.get_random("transactionId"),
					"planPayDate": Common.get_repaydate(12)[per - 1],
					"payTime": Common.get_time('-'),
					"successAmount": float(success_amount),
					"period": per
				}
			)
			for i in param['repaymentDetailList']:
				pay_detail = GetSqlData.get_repayment_detail(
					project_id=r.get('jfx_12_periods_projectId'),
					enviroment=env, period=per,
					repayment_plan_type=i['planCategory'])
				param['repaymentDetailList'][i].update(
					{
						"sourceRepaymentDetailId": Common.get_random("serviceSn"),
						"payAmount": float(pay_detail.get("cur_amount"))
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
				enviroment=env,
				product="cloudloan"
			)
			assert rep['resultCode'] == int(data[0]['resultCode'])

	# # @unittest.skipUnless(sys.argv[4] == "repayment", "条件成立时执行")
	# @unittest.skip("1")
	@allure.title("资金流水推送")
	@allure.severity("normal")
	@pytest.mark.offline_repay
	def test_114_capital_flow(self, r, env):
		"""资金流水推送"""
		data = excel_table_byname(self.excel, 'cash_push')
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			project_id=r.get("jfx_12_periods_projectId"), enviroment=env, period=1)
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"projectId": r.get("jfx_12_periods_projectId"),
				"sourceProjectId": r.get("jfx_12_periods_sourceProjectId"),
				"repaymentPlanId": Common.get_random("sourceProjectId"),
				"sucessAmount": float(success_amount),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"tradeTime": Common.get_time(),
				"finishTime": Common.get_time()
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
			enviroment=env,
			product="cloudloan"
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])


if __name__ == '__main__':
	pytest.main()