# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date: 2019-08-20
@describe:金服侠-牙医贷一期12期产品流程用例
"""

import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import allure
import pytest
from common.common_func import Common
from busi_assert.busi_asset import Assert
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData


@allure.feature("金服侠12期")
class TestJfx12PeriodTp:
	file = Config().get_item('File', 'jfx_mul_case_file')

	@allure.title("申请授信")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_100_credit_apply(self, r, env, red):
		"""额度授信"""
		data = excel_table_byname(self.file, 'credit_apply_data')
		r.setex(red["source_user_id"], 72000, Common.get_random("userid"))
		r.setex(red["transaction_id"], 72000, Common.get_random('transactionId'))
		r.setex(red["phone"], 72000, Common.get_random('phone'))
		r.setex(red["first_credit_date"], 72000, Common.get_time())
		param = json.loads(data[0]['param'])
		param['personalInfo'].update(
			{
				"cardNum": r.get(red["id_card"]),
				"custName": r.get(red["user_name"]),
				"phone": r.get(red["phone"]),
				"isDoctor": 0,
				"applicantClinicRelationship": 1
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time()})
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"serviceSn": Common.get_random('serviceSn'),
				"transactionId": r.get(red["transaction_id"])
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
			environment=env
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.setex(red["credit_id"], 72000, rep['content']['creditId'])
		r.setex(red["user_id"], 72000, rep['content']['userId'])

	@allure.title("授信结果查询")
	@allure.severity("normal")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_101_query_result(self, r, env, red):
		"""授信结果查询"""
		Assert.check_column("jfx_credit", env, r.get(red["credit_id"]))
		GetSqlData.credit_set(
			environment=env,
			credit_id=r.get(red["credit_id"])
		)
		data = excel_table_byname(self.file, 'credit_query_result')
		param = json.loads(data[0]['param'])
		param.update({"creditId": r.get(red["credit_id"])})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("用户额度查询")
	@allure.severity("normal")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_102_query_user_amount(self, r, env, red):
		"""用户额度查询"""
		data = excel_table_byname(self.file, 'query_user_amount')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"userId": r.get(red["user_id"])
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
			environment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("上传授信协议")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_103_sign_credit(self, r, env, red):
		"""上传授信协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get(red["source_user_id"]),
				"contractType": 1,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get(red["transaction_id"]),
				"associationId": r.get(red["credit_id"]),
				"content": Common.get_json_data('data', 'credit_sign.json').get("content")
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
			environment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("进件申请")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_104_project_apply(self, r, env, red):
		"""进件"""
		data = excel_table_byname(self.file, 'test_project')
		param = json.loads(data[0]['param'])
		r.setex(red["source_project_id"], 72000, Common.get_random('sourceProjectId'))
		param.update(
			{
				"sourceProjectId": r.get(red["source_project_id"]),
				"sourceUserId": r.get(red["source_user_id"]),
				"transactionId": r.get(red["transaction_id"])
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": r.get(red["id_card"]),
				"custName": r.get(red["user_name"]),
				"phone": r.get(red["phone"])
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
				"userInterestRate": 0.152156,
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
		r.setex(red["corporate_account_name"], 72000, param['cardInfo']['corporateAccountName'])
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']
		r.setex(red["project_id"], 72000, rep['content']['projectId'])

	@allure.title("进件结果查询")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_105_query_apply_result(self, r, env, red):
		"""进件结果查询"""
		Assert.check_column("jfx_project", env, r.get(red["project_id"]))
		GetSqlData.change_project_audit_status(
			project_id=r.get(red["project_id"]),
			environment=env
		)
		data = excel_table_byname(self.file, 'project_query_apply_result')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get(red["source_project_id"]),
				"projectId": r.get(red["project_id"])
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
			environment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("上传借款授信协议")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_106_sign_credit(self, r, env, red):
		"""上传借款授信协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get(red["source_user_id"]),
				"contractType": 5,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get(red["transaction_id"]),
				"associationId": r.get(red["project_id"]),
				"content": Common.get_json_data('data', 'credit_sign.json').get("content")
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
			environment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("上传借款合同")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_107_contract_sign(self, r, env, red):
		"""上传借款合同"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get(red["source_user_id"]),
				"contractType": 2,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get(red["transaction_id"]),
				"associationId": r.get(red["project_id"]),
				"content": Common.get_json_data('data', 'borrow_sign.json').get("content")
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
			environment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']

	@allure.title("放款申请")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_108_pfa(self, r, env, red):
		"""放款申请"""
		data = excel_table_byname(self.file, 'project_loan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get(red["source_project_id"]),
				"projectId": r.get(red["project_id"]),
				"sourceUserId": r.get(red["source_user_id"]),
				"serviceSn": Common.get_random('serviceSn'),
				"accountName": r.get(red["corporate_account_name"]),
				"bankCode": 86,
				"amount": 84920.00,
				"accountNo": "6214830173648711"  # 6227002432220410613
			}
		)
		r.setex(red["loan_service_sn"], 72000, param['serviceSn'])
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']
		GetSqlData.change_pay_status(
			environment=env,
			project_id=r.get(red["project_id"])
		)

	@allure.title("放款结果查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_109_pfa_query(self, r, env, red):
		"""放款结果查询"""
		GetSqlData.loan_set(
			environment=env,
			project_id=r.get(red["project_id"])
		)
		data = excel_table_byname(self.file, 'pfa_query')
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": r.get(red["loan_service_sn"])})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			environment=env,
			product="cloudloan"
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("提前结清试算")
	@allure.severity("blocker")
	def test_110_early_settlement(self, r, env, red):
		"""还款计划试算:提前结清"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"transactionId": r.get(red["source_project_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"projectId": r.get(red["project_id"]),
				"businessType": 2
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
			environment=env
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))
		r.setex(red["early_settlement_repayment_plan"], 72000, json.dumps(rep['content']['repaymentPlanList']))

	@allure.title("还款计划查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.settle
	def test_111_query_repayment_plan(self, r, env, red):
		"""还款计划查询"""
		data = excel_table_byname(self.file, 'repayment_plan')
		param = json.loads(data[0]['param'])
		param.update({"projectId": r.get(red["project_id"])})
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=env
		)
		assert int(data[0]['resultCode']) == rep['resultCode']
		r.setex(red["repayment_plan"], 72000, json.dumps(rep['content']['repaymentPlanList']))

	@allure.title("还款流水推送")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_112_repayment(self, r, env, red):
		"""还款流水推送"""
		data = excel_table_byname(self.file, 'repayment')
		param = json.loads(data[0]['param'])
		repayment_plan_list = r.get(red["repayment_plan"])
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
				"projectId": r.get(red["project_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"sourceUserId": r.get(red["source_user_id"]),
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
			environment=env,
			product="cloudloan"
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("全部结清")
	@allure.severity("blocker")
	@pytest.mark.settle
	def test_113_repayment(self, r, env, red):
		"""还款流水推送:全部结清"""
		data = excel_table_byname(self.file, 'repayment')
		param = json.loads(data[0]['param'])
		for per in range(1, 13):
			repayment_plan_list = r.get(red["repayment_plan"])
			success_amount = 0.00
			repayment_detail_list = []
			for i in json.loads(repayment_plan_list):
				if i['period'] == per:
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
					"projectId": r.get(red["project_id"]),
					"sourceProjectId": r.get(red["source_project_id"]),
					"sourceUserId": r.get(red["source_user_id"]),
					"serviceSn": Common.get_random("serviceSn"),
					"payTime": Common.get_time("-"),
					"successAmount": success_amount,
					"period": per
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
				environment=env,
				product="cloudloan"
			)
			assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("提前结清")
	@allure.severity("normal")
	def test_114_offline_settle(self, r, env, red):
		"""线下还款流水推送：提前全部结清"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_plan_date(project_id=r.get(red["project_id"]), environment=env,
														   repayment_plan_type=1, period=1)
		repayment_plan_list = r.get(red["early_settlement_repayment_plan"])
		success_amount = 0.00
		repayment_detail_list = []
		for i in json.loads(repayment_plan_list):
			plan_detail = {
				"sourceRepaymentDetailId": Common.get_random("transactionId"),
				"payAmount": i['amount'],
				"planCategory": i['repaymentPlanType']
			}
			success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
			repayment_detail_list.append(plan_detail)
		param.update(
			{
				"projectId": r.get(red["project_id"]),
				"transactionId": r.get(red["source_project_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
				"successAmount": success_amount,
				"repayType": 2,
				"period": json.loads(repayment_plan_list)[0]['period']
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
			product="cloudloan",
			environment=env
		)
		self.assertEqual(rep['resultCode'], int(data[0]['resultCode']))

	@allure.title("资金流水推送")
	@allure.severity("normal")
	@pytest.mark.offline_repay
	def test_115_capital_flow(self, r, env, red):
		"""资金流水推送"""
		data = excel_table_byname(self.file, 'cash_push')
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			project_id=r.get(red["project_id"]), environment=env, period=1)
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"projectId": r.get(red["project_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"repaymentPlanId": Common.get_random("sourceProjectId"),
				"successAmount": float(success_amount),
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
			environment=env,
			product="cloudloan"
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])


if __name__ == '__main__':
	pytest.main()
