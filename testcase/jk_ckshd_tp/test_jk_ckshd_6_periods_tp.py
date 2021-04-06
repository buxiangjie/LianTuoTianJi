# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 即科商户贷12期
"""
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import allure
from common.common_func import Common
from busi_assert.busi_asset import Asset
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData


@allure.feature("齿科商户贷6期")
class TestJkCkshd6PeriodsTp:
	file = Config().get_item('File', 'jk_ckshd_case_file')

	@allure.title("申请授信")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_100_credit_apply(self, env, r):
		"""额度授信"""
		data = excel_table_byname(self.file, 'credit')
		Common.p2p_get_userinfo('jk_ckshd_6_periods', env)
		r.mset(
			{
				"jk_ckshd_6_periods_sourceUserId": Common.get_random('userid'),
				'jk_ckshd_6_periods_transactionId': Common.get_random('transactionId'),
				"jk_ckshd_6_periods_phone": Common.get_random('phone'),
				"jk_ckshd_6_periods_firstCreditDate": Common.get_time()
			}
		)
		param = json.loads(data[0]['param'])
		param['personalInfo'].update(
			{
				"cardNum": r.get('jk_ckshd_6_periods_cardNum'),
				"custName": r.get('jk_ckshd_6_periods_custName'),
				"phone": r.get('jk_ckshd_6_periods_phone')
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time()})
		param['entityInfo']['unifiedSocialCreditCode'] = Common.get_random("businessLicenseNo")
		param.update(
			{
				"sourceUserId": r.get('jk_ckshd_6_periods_sourceUserId'),
				"serviceSn": Common.get_random('serviceSn'),
				"transactionId": r.get('jk_ckshd_6_periods_transactionId')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		# headers["X-TBC-SKIP-ENCRYPT"] = "true"
		# headers["X-TBC-SKIP-SIGN"] = "true"
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=env,
			prod_type="jkjr"
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.mset(
			{
				"jk_ckshd_6_periods_creditId": rep['content']['creditId'],
				"jk_ckshd_6_periods_userId": rep['content']['userId']
			}
		)

	@allure.title("授信结果查询")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_101_query_result(self, env, r):
		"""授信结果查询"""
		Asset.check_column("jk_ckshd_credit", env, r.get("jk_ckshd_6_periods_creditId"))
		GetSqlData.credit_set(
			environment=env,
			credit_id=r.get("jk_ckshd_6_periods_creditId")
		)
		data = excel_table_byname(self.file, 'query_result')
		param = json.loads(data[0]['param'])
		param.update({"creditId": r.get('jk_ckshd_6_periods_creditId')})
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
		assert int(data[0]['resultCode']), rep['resultCode']
		assert rep['content']['creditStatus'], 1

	@allure.title("用户额度查询")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_102_query_user_amount(self, env, r):
		"""用户额度查询"""
		data = excel_table_byname(self.file, 'query_user_amount')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get('jk_ckshd_6_periods_sourceUserId'),
				"userId": r.get('jk_ckshd_6_periods_userId')
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
		assert int(data[0]['resultCode']), rep['resultCode']

	@allure.title("上传授信协议")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_103_sign_credit(self, env, r):
		"""上传授信协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'credit_sign.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('jk_ckshd_6_periods_sourceUserId'),
				"contractType": 1,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get('jk_ckshd_6_periods_transactionId'),
				"associationId": r.get('jk_ckshd_6_periods_creditId')
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
		assert int(data[0]['resultCode']), rep['resultCode']

	@allure.title("进件申请")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.project_cancel
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_104_apply(self, env, r):
		"""进件"""
		data = excel_table_byname(self.file, 'apply')
		r.mset(
			{
				"jk_ckshd_6_periods_transactionId": Common.get_random('transactionId'),
				"jk_ckshd_6_periods_sourceProjectId": Common.get_random('sourceProjectId'),
			}
		)
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get('jk_ckshd_6_periods_sourceProjectId'),
				"sourceUserId": r.get('jk_ckshd_6_periods_sourceUserId'),
				# "transactionId": r.get('jk_ckshd_6_periods_transactionId')
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time("-"),
				"applyAmount": 50000,
				"applyTerm": 12,
			}
		)
		param['loanInfo'].update(
			{
				"loanAmount": 50000,
				"loanTerm": 12,
				"assetInterestRate": 0.09,
				"userInterestRate": 0.16,
				"discountRate": 0.01
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": r.get('jk_ckshd_6_periods_cardNum'),
				"custName": r.get('jk_ckshd_6_periods_custName'),
				"phone": r.get('jk_ckshd_6_periods_phone')
			}
		)
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		# headers["X-TBC-SKIP-ENCRYPT"] = "true"
		# headers["X-TBC-SKIP-SIGN"] = "true"
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=env,
			prod_type="jkjr"
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.set('jk_ckshd_6_periods_projectId', rep['content']['projectId'])

	@allure.title("进件取消")
	@allure.severity("critical")
	@pytest.mark.project_cancel
	def test_105_cancel(self, env, r):
		"""进件取消"""
		data = excel_table_byname(self.file, 'cancel')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get('jk_ckshd_6_periods_sourceProjectId'),
				"projectId": r.get('jk_ckshd_6_periods_projectId')
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
	def test_106_query_apply_result(self, env, r):
		"""进件结果查询"""
		Asset.check_column("jk_ckshd_project", env, r.get("jk_ckshd_6_periods_projectId"))
		GetSqlData.change_project_audit_status(
			project_id=r.get('jk_ckshd_6_periods_projectId'),
			environment=env
		)
		data = excel_table_byname(self.file, 'query_apply_result')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get('jk_ckshd_6_periods_sourceProjectId'),
				"projectId": r.get('jk_ckshd_6_periods_projectId')
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
		assert rep['content']['auditStatus'], 2

	@allure.title("上传借款协议")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_107_sign_borrow(self, env, r):
		"""上传借款协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('jk_ckshd_6_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"contractType": 2,
				"transactionId": r.get('jk_ckshd_6_periods_transactionId'),
				"associationId": r.get('jk_ckshd_6_periods_projectId'),
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
		r.set("jk_ckshd_6_periods_contractId", rep['content']['contractId'])

	@allure.title("上传图片")
	@allure.severity("trivial")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_108_image_upload(self, env, r):
		"""上传图片"""
		data = excel_table_byname(self.file, 'image_upload')
		param = json.loads(data[0]['param'])
		param.update({"associationId": r.get('jk_ckshd_6_periods_projectId')})
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
	def test_109_contact_query(self, env, r):
		"""合同结果查询:获取签章后的借款协议"""
		data = excel_table_byname(self.file, 'contract_query')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"associationId": r.get('jk_ckshd_6_periods_projectId'),
				"serviceSn": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": r.get("jk_ckshd_6_periods_sourceUserId"),
				"contractId": r.get("jk_ckshd_6_periods_contractId")
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
	def test_110_calculate(self, env, r):
		"""还款计划试算（未放款）:正常还款"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get("jk_ckshd_6_periods_sourceUserId"),
				"transactionId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"sourceProjectId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"projectId": r.get("jk_ckshd_6_periods_projectId")
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
	def test_111_deduction_share_sign(self, env, r):
		"""协议支付号共享"""
		data = excel_table_byname(self.file, 'deduction_share_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": r.get("jk_ckshd_6_periods_sourceUserId"),
				"transactionId": Common.get_random("transactionId"),
				"sourceProjectId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"projectId": r.get("jk_ckshd_6_periods_projectId"),
				"name": r.get("jk_ckshd_6_periods_custName"),
				"cardNo": r.get("jk_ckshd_6_periods_cardNum"),
				# "bankNo": "6217002200003225702",
				"bankNo": r.get("jk_ckshd_6_periods_bankcard"),
				"bankPhone": r.get("jk_ckshd_6_periods_phone"),
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
			prod_type="wxjk"
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.set("jk_ckshd_6_periods_signId", rep["content"]["signId"])

	@allure.title("委托划扣协议上传")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_112_deduction_share_sign(self, env, r):
		"""委托划扣协议上传"""
		data = excel_table_byname(self.file, 'upload')
		param = Common.get_json_data('data', 'rong_pay_upload.json')
		param.update(
			{
				"associationId": r.get("jk_ckshd_6_periods_signId"),
				"requestId": Common.get_random("serviceSn"),
				"sourceContractId": Common.get_random("serviceSn"),
				"sourceUserId": r.get("jk_ckshd_6_periods_sourceUserId")
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
			prod_type="wxjk"
		)
		assert rep['code'], int(data[0]['resultCode'])

	@allure.title("放款申请")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_113_loan_pfa(self, env, r):
		"""放款申请"""
		data = excel_table_byname(self.file, 'loan_pfa')
		param = json.loads(data[0]['param'])
		r.set("jk_ckshd_6_periods_loan_serviceSn", Common.get_random("serviceSn"))
		param.update(
			{
				"sourceProjectId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"projectId": r.get("jk_ckshd_6_periods_projectId"),
				"sourceUserId": r.get("jk_ckshd_6_periods_sourceUserId"),
				"serviceSn": r.get("jk_ckshd_6_periods_loan_serviceSn"),
				"id": r.get('jk_ckshd_6_periods_cardNum'),
				"accountName": r.get("jk_ckshd_6_periods_custName"),
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
			project_id=r.get('jk_ckshd_6_periods_projectId')
		)

	@allure.title("放款结果查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_114_loan_query(self, env, r):
		"""放款结果查询"""
		GetSqlData.loan_set(environment=env, project_id=r.get('jk_ckshd_6_periods_projectId'))
		data = excel_table_byname(self.file, 'pfa_query')
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": r.get("jk_ckshd_6_periods_loan_serviceSn")})
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
		assert rep['content']['projectLoanStatus'], 3

	@allure.title("国投云贷还款计划查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_115_query_repayment_plan(self, env, r):
		"""国投云贷还款计划查询"""
		data = excel_table_byname(self.file, 'query_repayment_plan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"transactionId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"projectId": r.get("jk_ckshd_6_periods_projectId")
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
		r.set("jk_ckshd_6_periods_repayment_plan", json.dumps(rep['content']['repaymentPlanList']))

	@allure.title("还款计划试算:提前结清")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_116_calculate(self, env, r):
		"""还款计划试算:提前结清"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get("jk_ckshd_6_periods_sourceUserId"),
				"transactionId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"sourceProjectId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"projectId": r.get("jk_ckshd_6_periods_projectId"),
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
		r.set(
			"jk_ckshd_6_periods_early_settlement_repayment_plan",
			json.dumps(rep['content']['repaymentPlanList'])
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("还款计划试算:退货")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_117_calculate(self, env, r):
		"""还款计划试算:退货"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get("jk_ckshd_6_periods_sourceUserId"),
				"transactionId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"sourceProjectId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"projectId": r.get("jk_ckshd_6_periods_projectId"),
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
		r.set(
			"jk_ckshd_6_periods_return_repayment_plan",
			json.dumps(rep['content']['repaymentPlanList'])
		)

	@allure.title("线下还款流水推送：正常还一期")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_118_offline_repay_repayment(self, env, r):
		"""线下还款流水推送：正常还一期"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		period = 1
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=r.get("jk_ckshd_6_periods_projectId"),
			environment=env,
			period=period,
			repayment_plan_type=1
		)
		repayment_plan_list = r.get("jk_ckshd_6_periods_repayment_plan")
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
				"projectId": r.get("jk_ckshd_6_periods_projectId"),
				"transactionId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"sourceProjectId": r.get("jk_ckshd_6_periods_sourceProjectId"),
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

	@allure.title("线下还款流水推送：提前全部结清")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_119_offline_repay_early_settlement(self, env, r):
		"""线下还款流水推送：提前全部结清"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=r.get("jk_ckshd_6_periods_projectId"),
			environment=env,
			period=1,
			repayment_plan_type=1
		)
		repayment_plan_list = json.loads(r.get("jk_ckshd_6_periods_early_settlement_repayment_plan"))
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
				"projectId": r.get("jk_ckshd_6_periods_projectId"),
				"transactionId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"sourceProjectId": r.get("jk_ckshd_6_periods_sourceProjectId"),
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

	@allure.title("线下还款流水推送：退货")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_120_offline_return(self, env, r):
		"""线下还款流水推送：退货"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=r.get("jk_ckshd_6_periods_projectId"),
			environment=env,
			period=1,
			repayment_plan_type=1
		)
		repayment_plan_list = json.loads(r.get("jk_ckshd_6_periods_return_repayment_plan"))
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
				"projectId": r.get("jk_ckshd_6_periods_projectId"),
				"transactionId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"sourceProjectId": r.get("jk_ckshd_6_periods_sourceProjectId"),
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
	@pytest.mark.asset
	@pytest.mark.offline_repay
	def test_121_capital_flow(self, env, r):
		"""资金流水推送"""
		data = excel_table_byname(self.file, 'cash_push')
		param = json.loads(data[0]['param'])
		success_amount = GetSqlData.get_repayment_amount(
			project_id=r.get("jk_ckshd_6_periods_projectId"),
			environment=env,
			period=1
		)
		param.update(
			{
				"serviceSn": Common.get_random("serviceSn"),
				"projectId": r.get("jk_ckshd_6_periods_projectId"),
				"sourceProjectId": r.get("jk_ckshd_6_periods_sourceProjectId"),
				"repaymentPlanId": Common.get_random("sourceProjectId"),
				"sucessAmount": success_amount,
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

	@allure.title("上传采购凭证")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_122_sign_purchase_vouchers(self, env, r):
		"""上传采购凭证"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('jk_ckshd_6_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get('jk_ckshd_6_periods_transactionId'),
				"associationId": r.get('jk_ckshd_6_periods_projectId'),
				"contractType": 15,
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
		assert rep['resultCode'] == int(data[0]['resultCode'])