# -*- coding: UTF-8 -*-
"""
@auth:卜祥杰
@date:2019-10-22 09:39:00
@describe: 任买医美三期进件-放款流程
"""
import os
import json
import sys

from busi_assert.busi_asset import Assert

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import allure
from common.common_func import Common
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData


@allure.feature("任买3期流程")
class TestRmkj3Tp:
	file = Config().get_item('File', 'rmkj_case_file')

	@allure.title("任买进件")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.settle
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	def test_100_apply(self, r, env, red):
		"""进件申请"""
		data = excel_table_byname(self.file, 'apply')
		r.setex(red["source_user_id"], 72000, Common.get_random("userid"))
		r.setex(red["transaction_id"], 72000, Common.get_random('transactionId'))
		r.setex(red["phone"], 72000, Common.get_random('phone'))
		r.setex(red["source_project_id"], 72000, Common.get_random('sourceProjectId'))
		param = json.loads(data[0]['param'])
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
				"applyTime": Common.get_time("-"),
				"applyTerm": 3
			}
		)
		param['loanInfo'].update(
			{
				"loanTerm": 3
			}
		)
		param['cardInfo'].update(
			{
				"unifiedSocialCreditCode": Common.get_random("businessLicenseNo"),
				"corporateAccountName": "南京车置宝网络技术有限公司",
				"bankCode": 34
			}
		)
		param['bindingCardInfo'].update(
			{
				"bankCardNo": r.get(red["bank_card"]),
				"bankPhone": r.get(red["phone"]),
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
		r.setex(red["project_id"], 72000, rep['content']['projectId'])

	@allure.title("上传借款授信协议")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_101_sign_credit(self, r, env, red):
		"""上传授信协议"""
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
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("进件结果查询")
	@allure.severity("trivial")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_102_query_apply_result(self, r, env, red):
		"""进件结果查询"""
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
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_103_sign_borrow(self, r, env, red):
		"""上传借款协议"""
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
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.setex(red["contract_id"], 72000, rep['content']['contractId'])

	@allure.title("上传还款计划文件")
	@allure.severity("minor")
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_1033_sign_repayment(self, r, env, red):
		"""上传还款计划文件"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get(red["source_user_id"]),
				"contractType": 6,
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
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("上传医疗美容图片")
	@allure.severity("trivial")
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_104_image_upload(self, r, env, red):
		"""上传医疗美容图片"""
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
	@allure.severity("trivial")
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_105_contact_query(self, r, env, red):
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

	@allure.title("预签约")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_106_sign(self, r, env, red):
		"""预签约"""
		data = excel_table_byname(self.file, 'sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"requestId": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": r.get(red["source_user_id"]),
				# "name": r.get("rmkj_3_periods_custName"),
				# "cardNo": r.get("rmkj_3_periods_cardNum"),
				# "bankNo": r.get("rmkj_3_periods_bankcard"),
				# "mobile": r.get("rmkj_3_periods_phone"),
				"bankNo": "6214850219949549",
				"name": "幸福",
				"mobile": "18689262774",
				"cardNo": "370613198705308692"
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
			product='gateway',
			environment=env,
			prod_type="rmkj"
		)
		assert rep['code'] == int(data[0]['resultCode'])
		r.setex(red["sign_id"], 72000, rep['data']['signTaskId'])

	@allure.title("确认签约")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_107_confirm(self, r, env, red):
		"""确认签约"""
		data = excel_table_byname(self.file, 'confirm')
		param = Common.get_json_data("data", "rmkj_confirm.json")
		param.update(
			{
				"requestId": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": r.get(red["source_user_id"]),
				"signTaskId": r.get(red["sign_id"]),
				"smsCode": "849201"
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
			product='gateway',
			environment=env,
			prod_type="rmkj"
		)
		assert rep['code'] == int(data[0]['resultCode'])
		assert rep['data']['code'] in (60103, 3)

	@allure.title("绑卡结果查询")
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_108_query_sign(self, r, env, red):
		"""绑卡结果查询"""
		data = excel_table_byname(self.file, 'query_sign')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"requestId": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": r.get(red["source_user_id"]),
				"signTaskId": r.get(red["sign_id"])
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
			product='gateway',
			environment=env,
			prod_type="rmkj"
		)
		assert rep['code'] == int(data[0]['resultCode'])
		assert rep['data']['code'] in (60103, 3)

	@allure.title("还款卡推送")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_109_card_change(self, r, env, red):
		"""还款卡推送"""
		data = excel_table_byname(self.file, 'card_change')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"projectId": r.get(red["project_id"]),
				# "name": r.get("rmkj_3_periods_custName"),
				# "cardNo": r.get("rmkj_3_periods_cardNum"),
				# "bankNo": r.get("rmkj_3_periods_bankcard"),
				# "mobile": r.get("rmkj_3_periods_phone"),
				"bankNo": "6214850219949549",
				"name": "幸福",
				"mobile": "18689262774",
				"cardNo": "370613198705308692",
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

	@allure.title("放款前还款计划试算")
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_1091_calculate(self, r, env, red):
		"""还款计划试算（未放款）:正常还款"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"transactionId": r.get(red["source_project_id"]),
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

	@allure.title("放款申请")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_110_loan_pfa(self, r, env, red):
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
				"accountName": "南京车置宝网络技术有限公司",
				"openAccountProvince": 320000,
				"openAccountCity": 320100,
				"openAccountBankNameSub": "南京支行",
				"bankCode": 34
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
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_111_loan_query(self, r, env, red):
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
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.returns
	@pytest.mark.settle
	def test_112_query_repayment_plan(self, r, env, red):
		"""国投云贷还款计划查询"""
		data = excel_table_byname(self.file, 'query_repayment_plan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"transactionId": r.get(red["source_project_id"]),
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
		Assert.check_repayment(False, env, r.get(red["project_id"]))
		r.setex(red["repayment_plan"], 72000, json.dumps(rep['content']['repaymentPlanList']))

	@allure.title("提前结清试算")
	@allure.severity("blocker")
	@pytest.mark.settle_in_advance
	@pytest.mark.offline_settle_in_advance
	def test_113_calculate(self, r, env, red):
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
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.setex(red["early_settlement_repayment_plan"], 72000, json.dumps(rep['content']['repaymentPlanList']))

	@allure.title("退货试算")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_114_calculate(self, r, env, red):
		"""还款计划试算:退货"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"transactionId": r.get(red["source_project_id"]),
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

	@allure.title("主动还款一期")
	@allure.severity("blocker")
	@pytest.mark.repayment
	def test_115_deduction_apply(self, r, env, red):
		"""主动还款:正常还一期"""
		data = excel_table_byname(self.file, 'deduction_apply')
		param = json.loads(data[0]['param'])
		repayment_plan_list = r.get(red["repayment_plan"])
		success_amount = 0.00
		repayment_detail_list = []
		period = 1
		for i in json.loads(repayment_plan_list):
			if i['period'] == period:
				plan_detail = {
					"period": period,
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
		headers["X-TBC-SKIP-SIGN"] = "true"
		rep = Common.response(
			faceaddr=data[0]['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=env
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])
		Assert.check_repayment(True, env, r.get(red["project_id"]), param)
		r.setex(red["deduction_task_id"], 72000, rep['content']['deductionTaskId'])

	@allure.title("主动还款-连续还款结清")
	@allure.severity("blocker")
	@pytest.mark.settle
	def test_116_deduction_apply_all_periods(self, r, env, red):
		"""主动还款:连续还款整笔结清"""
		data = excel_table_byname(self.file, 'deduction_apply')
		param = json.loads(data[0]['param'])
		repayment_plan_list = r.get(red["repayment_plan"])
		maturity = GetSqlData.get_maturity(
			project_id=r.get(red["project_id"]),
			environment=env
		)
		for period in range(maturity):
			period = period + 1
			success_amount = 0.00
			repayment_detail_list = []
			for i in json.loads(repayment_plan_list):
				if i['period'] == period:
					plan_detail = {
						"period": i['period'],
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
				product="cloudloan",
				environment=env
			)
			assert rep['resultCode'] == int(data[0]['resultCode'])
			Assert.check_repayment(True, env, r.get(red["project_id"]), param)
			r.setex(red["deduction_task_id"], 72000, rep['content']['deductionTaskId'])

	@allure.title("主动还款-提前全部结清")
	@allure.severity("blocker")
	@pytest.mark.settle_in_advance
	def test_117_deduction_settle_in_advance(self, r, env, red):
		"""主动还款:提前全部结清"""
		data = excel_table_byname(self.file, 'deduction_apply')
		param = json.loads(data[0]['param'])
		repayment_plan_list = r.get(red["early_settlement_repayment_plan"])
		success_amount = 0.00
		repayment_detail_list = []
		for i in json.loads(repayment_plan_list):
			plan_detail = {
				"period": i['period'],
				"payAmount": i['amount'],
				"planCategory": i['repaymentPlanType']
			}
			success_amount = round(success_amount + plan_detail.get("payAmount"), 2)
			repayment_detail_list.append(plan_detail)
		param.update({
			"sourceRequestId": Common.get_random("requestNum"),
			"projectId": r.get(red["project_id"]),
			"sourceProjectId": r.get(red["source_project_id"]),
			"sourceUserId": r.get(red["source_user_id"]),
			"serviceSn": Common.get_random("serviceSn"),
			"repayType": 2,
			"payTime": Common.get_time("-"),
			"successAmount": success_amount,
			"period": json.loads(repayment_plan_list)[0]['period']
		})
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
		Assert.check_repayment(True, env, r.get(red["project_id"]), param)
		r.setex(red["deduction_task_id"], 72000, rep['content']['deductionTaskId'])

	@allure.severity("blocker")
	def test_118_offline_partial(self, r, env, red):
		"""线下还款:部分还款"""
		data = excel_table_byname(self.file, 'offline_partial')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceRequestId": Common.get_random("requestNum"),
				"sourceRepaymentId": Common.get_random("requestNum"),
				"projectId": r.get(red["project_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"sourceUserId": r.get(red["source_user_id"]),
				"serviceSn": Common.get_random("serviceSn"),
				"payTime": Common.get_time("-"),
				"successAmount": 40,
				"period": 1
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

	@allure.title("主动还款结果查询")
	@allure.severity("blocker")
	@pytest.mark.repayment
	@pytest.mark.settle_in_advance
	@pytest.mark.settle
	def test_119_deduction_query(self, r, env, red):
		"""主动还款结果查询"""
		data = excel_table_byname(self.file, 'deduction_query')
		param = json.loads(data[0]['param'])
		param.update({"deductionTaskId": r.get(red["deduction_task_id"])})
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

	@allure.title("线下还款一期")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_120_offline_repay_repayment(self, r, env, red):
		"""线下还款流水推送：正常还一期"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		period = 1
		plan_pay_date = GetSqlData.get_repayment_plan_date(
			project_id=r.get(red["project_id"]),
			environment=env,
			repayment_plan_type=1,
			period=period
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
				"transactionId": r.get(red["source_project_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": plan_pay_date['plan_pay_date'],
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
		Assert.check_repayment(True, env, r.get(red["project_id"]), param)

	@allure.title("提前全部结清流水推送")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_121_offline_repay_early_settlement(self, r, env, red):
		"""线下还款流水推送：提前全部结清"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_plan_date(
			project_id=r.get(red["project_id"]),
			environment=env,
			repayment_plan_type=1,
			period=1
		)
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
				"planPayDate": plan_pay_date.get('plan_pay_date'),
				"successAmount": success_amount,
				"repayType": 2,
				"period": json.loads(repayment_plan_list)[0]['period'],
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
		Assert.check_repayment(True, env, r.get(red["project_id"]), param)

	@allure.title("退货流水推送")
	@allure.severity("blocker")
	@pytest.mark.returns
	def test_122_refunds(self, r, env, red):
		"""线下还款流水推送：退货"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_plan_date(
			project_id=r.get(red["project_id"]),
			environment=env,
			repayment_plan_type=1,
			period=1
		)
		repayment_plan_list = r.get(red["return_repayment_plan"])
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
				"planPayDate": plan_pay_date['plan_pay_date'],
				"successAmount": success_amount,
				"repayType": 3,
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
		Assert.check_repayment(True, env, r.get(red["project_id"]), param)


if __name__ == '__main__':
	pytest.main()
