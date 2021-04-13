# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2021-03-25 11:26:00
@describe: 即科宠物商户贷6期
"""
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import allure

from common.common_func import Common
from busi_assert.busi_asset import Assert
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData


@allure.feature("宠物商户贷6期")
@pytest.mark.skip("业务未上线")
class TestJkCwShd6PeriodsTp:
	file = Config().get_item('File', 'jk_cwshd_case_file')

	@allure.title("申请授信")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_100_credit_apply(self, env, r, red):
		"""额度授信"""
		data = excel_table_byname(self.file, 'credit')
		r.setex(red["source_user_id"], 72000, Common.get_random("userid"))
		r.setex(red["transaction_id"], 72000, Common.get_random('transactionId'))
		r.setex(red["phone"], 72000, Common.get_random('phone'))
		r.setex(red["first_credit_date"], 72000, Common.get_time())
		param = json.loads(data[0]['param'])
		param['personalInfo'].update(
			{
				"cardNum": r.get(red["id_card"]),
				"custName": r.get(red["user_name"]),
				"phone": r.get(red["phone"])
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time()})
		param['entityInfo']['unifiedSocialCreditCode'] = Common.get_random("businessLicenseNo")
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"serviceSn": Common.get_random('serviceSn'),
				"transactionId": r.get(red["transaction_id"])
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
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.setex(red["credit_id"], 72000, rep['content']['creditId'])
		r.setex(red["user_id"], 72000, rep['content']['userId'])

	@allure.title("授信结果查询")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_101_query_result(self, env, r, red):
		"""授信结果查询"""
		GetSqlData.credit_set(
			environment=env,
			credit_id=r.get(red["credit_id"])
		)
		data = excel_table_byname(self.file, 'query_result')
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
		assert rep['content']['creditStatus'] == 1

	@allure.title("用户额度查询")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_102_query_user_amount(self, env, r, red):
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
	@pytest.mark.project
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_103_sign_credit(self, env, r, red):
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
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_104_apply(self, env, r, red):
		"""进件"""
		data = excel_table_byname(self.file, 'apply')
		r.setex(red["source_project_id"], 72000, Common.get_random('sourceProjectId'))
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get(red["source_project_id"]),
				"sourceUserId": r.get(red["source_user_id"]),
				"transactionId": r.get(red["transaction_id"])
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time("-"),
				"applyAmount": 30000,
				"applyTerm": 6,
			}
		)
		param['loanInfo'].update(
			{
				"loanAmount": 30000,
				"loanTerm": 6,
				"assetInterestRate": 0.10,
				"userInterestRate": 0.10,
				"discountRate": 0
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": r.get(red["id_card"]),
				"custName": r.get(red["user_name"]),
				"phone": r.get(red["phone"])
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
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.set(red["project_id"], rep['content']['projectId'])

	@allure.title("进件取消")
	@allure.severity("blocker")
	@pytest.mark.project_cancel
	def test_105_cancel(self, env, r, red):
		"""进件取消"""
		data = excel_table_byname(self.file, 'cancel')
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
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("进件结果查询")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_106_query_apply_result(self, env, r, red):
		"""进件结果查询"""
		Assert.check_column("jk_cwshd_project", env, r.get(red["project_id"]))
		GetSqlData.change_project_audit_status(
			project_id=r.get(red["project_id"]),
			environment=env
		)
		data = excel_table_byname(self.file, 'query_apply_result')
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
		assert rep['resultCode'] == int(data[0]['resultCode'])
		assert rep['content']['auditStatus'] == 2

	@allure.title("上传借款协议")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_107_sign_borrow(self, env, r, red):
		"""上传借款协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get(red["source_user_id"]),
				"sourceContractId": Common.get_random('userid'),
				"contractType": 2,
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
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.setex(red["contract_id"], 72000, rep['content']['contractId'])

	@allure.title("上传图片")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_108_image_upload(self, env, r, red):
		"""上传图片"""
		data = excel_table_byname(self.file, 'image_upload')
		param = json.loads(data[0]['param'])
		param.update({"associationId": r.get(red["project_id"])})
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

	@allure.title("合同结果查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_109_contact_query(self, env, r, red):
		"""合同结果查询:获取签章后的借款协议"""
		data = excel_table_byname(self.file, 'contract_query')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"associationId": r.get(red["project_id"]),
				"serviceSn": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": r.get(red["source_user_id"]),
				"contractId": r.get(red["contract_id"])
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
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("还款计划试算(未放款)")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_110_calculate(self, env, r, red):
		"""还款计划试算（未放款）:正常还款"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"transactionId": r.get(red["transaction_id"]),
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
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("协议支付号共享")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_111_deduction_share_sign(self, env, r, red):
		"""协议支付号共享"""
		data = excel_table_byname(self.file, 'deduction_share_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": r.get(red["source_user_id"]),
				"transactionId": Common.get_random("transactionId"),
				"sourceProjectId": r.get(red["source_project_id"]),
				"projectId": r.get(red["project_id"]),
				"name": r.get(red["user_name"]),
				"cardNo": r.get(red["id_card"]),
				# "bankNo": "6217002200003225702",
				"bankNo": r.get(red["bank_card"]),
				"bankPhone": r.get(red["phone"]),
				"signNo": Common.get_random("businessLicenseNo"),
				"authLetterNo": Common.get_random("transactionId")
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		headers["X-TBC-SKIP-SIGN"] = 'true'
		headers["X-TBC-SKIP-ENCRYPT"] = 'true'
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="gateway",
			environment=env,
			prod_type="jkjr"
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.setex(red["sign_id"], 72000, rep["content"]["signId"])

	@allure.title("委托划扣协议上传")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_112_deduction_share_sign(self, env, r, red):
		"""委托划扣协议上传"""
		data = excel_table_byname(self.file, 'upload')
		param = Common.get_json_data('data', 'rong_pay_upload.json')
		param.update(
			{
				"associationId": r.get(red["sign_id"]),
				"requestId": Common.get_random("serviceSn"),
				"sourceContractId": Common.get_random("serviceSn"),
				"sourceUserId": r.get(red["source_user_id"])
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		headers["X-TBC-SKIP-SIGN"] = 'true'
		headers["X-TBC-SKIP-ENCRYPT"] = 'true'
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="gateway",
			environment=env,
			prod_type="jkjr"
		)
		assert rep['code'] == int(data[0]['resultCode'])

	@allure.title("放款申请")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_113_loan_pfa(self, env, r, red):
		"""放款申请"""
		data = excel_table_byname(self.file, 'loan_pfa')
		param = json.loads(data[0]['param'])
		r.setex(red["loan_service_sn"], 72000, Common.get_random("serviceSn"))
		param.update(
			{
				"sourceProjectId": r.get(red["source_project_id"]),
				"projectId": r.get(red["project_id"]),
				"sourceUserId": r.get(red["source_user_id"]),
				"serviceSn": r.get(red["loan_service_sn"]),
				"id": r.get(red["id_card"]),
				"accountName": r.get(red["user_name"]),
				"amount": 50000
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
		assert rep['resultCode'] == int(data[0]['resultCode'])
		# 修改支付表中的品钛返回code
		GetSqlData.change_pay_status(
			environment=env,
			project_id=r.get(red["project_id"])
		)

	@allure.title("放款结果查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_114_loan_query(self, env, r, red):
		"""放款结果查询"""
		GetSqlData.loan_set(environment=env, project_id=r.get(red["project_id"]))
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
			product="cloudloan",
			environment=env
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])
		assert rep['content']['projectLoanStatus'] == 3

	@allure.title("还款计划查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_115_query_repayment_plan(self, env, r, red):
		"""国投云贷还款计划查询"""
		data = excel_table_byname(self.file, 'query_repayment_plan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"transactionId": r.get(red["transaction_id"]),
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
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.setex(red["repayment_plan"], 72000, json.dumps(rep['content']['repaymentPlanList']))

	@allure.title("提前结清试算")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_116_calculate(self, env, r, red):
		"""还款计划试算:提前结清"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"transactionId": r.get(red["transaction_id"]),
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
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.setex(red["early_settlement_repayment_plan"], 72000, json.dumps(rep['content']['repaymentPlanList']))

	@allure.title("退货试算")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_117_calculate(self, env, r, red):
		"""还款计划试算:退货"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"transactionId": r.get(red["transaction_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"projectId": r.get(red["project_id"]),
				"businessType": 3
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
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.setex(red["return_repayment_plan"], 72000, json.dumps(rep['content']['repaymentPlanList']))

	@allure.title("还款流水推送")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_118_offline_repay_repayment(self, env, r, red):
		"""线下还款流水推送：正常还一期"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		period = 1
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=r.get(red["project_id"]),
			environment=env,
			period=period,
			repayment_plan_type=1
		)
		repayment_plan_list = r.get(red["repayment_plan"])
		success_amount = 0.00
		repayment_detail_list = []
		for i in json.loads(repayment_plan_list):
			if i['period'] == period:
				plan_detail = {
					"sourceRepaymentDetailId": Common.get_random("transactionId"),
					"payAmount": i['restAmount'],
					"planCategory": i['repaymentPlanType']
				}
				success_amount = round(success_amount + float(plan_detail.get("payAmount")), 2)
				repayment_detail_list.append(plan_detail)
		param.update(
			{
				"projectId": r.get(red["project_id"]),
				"transactionId": r.get(red["transaction_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
				"successAmount": success_amount,
				"payTime": Common.get_time("-"),
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
			product="cloudloan",
			environment=env
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("提前结清流水推送")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_119_offline_repay_early_settlement(self, env, r, red):
		"""线下还款流水推送：提前全部结清"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=r.get(red["project_id"]),
			environment=env,
			period=1,
			repayment_plan_type=1
		)
		repayment_plan_list = json.loads(r.get(red["early_settlement_repayment_plan"]))
		success_amount = 0.00
		repayment_detail_list = []
		for i in repayment_plan_list:
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
				"transactionId": r.get(red["transaction_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
				"successAmount": success_amount,
				"repayType": 2,
				"period": repayment_plan_list[0]['period'],
				"payTime": Common.get_time("-")
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
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("退货流水推送")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_120_offline_return(self, env, r, red):
		"""线下还款流水推送：退货"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=r.get(red["project_id"]),
			environment=env,
			period=1,
			repayment_plan_type=1
		)
		repayment_plan_list = json.loads(r.get(red["return_repayment_plan"]))
		success_amount = 0.00
		repayment_detail_list = []
		for i in repayment_plan_list:
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
				"transactionId": r.get(red["transaction_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
				"successAmount": success_amount,
				"repayType": 3,
				"period": repayment_plan_list[0]['period'],
				"payTime": Common.get_time("-")
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
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("资金流水推送")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_121_capital_flow(self, env, r, red):
		"""资金流水推送"""
		data = excel_table_byname(self.file, 'cash_push')
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			project_id=r.get(red["project_id"]),
			environment=env,
			period=1
		)
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"projectId": r.get(red["project_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"repaymentPlanId": Common.get_random("sourceProjectId"),
				"successAmount": success_amount,
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
