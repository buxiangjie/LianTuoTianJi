# -*- coding: UTF-8 -*-
"""
@auth:卜祥杰
@date:2020-09-21 15:50:00
@describe: 即分期教育V2 18期
"""
import os
import json
import sys

from busi_assert.busi_asset import Assert
from common.universal import Universal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import allure
import pytest

from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

logger = Logger(logger="test_jfqjyv2_18_periods_tp").getlog()


@allure.feature("即分期教育V2 18期")
class TestJfqjyv218Tp:
	file = Config().get_item('File', 'jfq_case_file')

	@allure.title("进件申请")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.overdue
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.compensation
	@pytest.mark.repurchase
	def test_100_apply(self, r, env, red):
		"""进件"""
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
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time("-"),
				"applyAmount": 33333.33,
				"applyTerm": 18,
				"productCode": "FQ_JK_JFQJYV2"
			}
		)
		param['loanInfo'].update(
			{
				"loanAmount": 33333.33,
				"loanTerm": 18,
				"assetInterestRate": 0.153,
				"userInterestRate": 0.083646
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": r.get(red["id_card"]),
				"custName": r.get(red["user_name"]),
				"phone": r.get(red["phone"])
			}
		)
		param['applyInfo'].update({"applyTime": Common.get_time("-")})
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

	@allure.title("上传授信协议")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.overdue
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.compensation
	@pytest.mark.repurchase
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
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.overdue
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.compensation
	@pytest.mark.repurchase
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
	@pytest.mark.offline_repay
	@pytest.mark.overdue
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.compensation
	@pytest.mark.repurchase
	def test_103_sign_borrow(self, r, env, red):
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
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.overdue
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.compensation
	@pytest.mark.repurchase
	def test_105_image_upload(self, r, env, red):
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

	@allure.title("签章结果查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.overdue
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.compensation
	@pytest.mark.repurchase
	def test_106_contact_query(self, r, env, red):
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

	@allure.title("还款计划试算")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.overdue
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.compensation
	@pytest.mark.repurchase
	def test_107_calculate(self, r, env, red):
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

	@allure.title("放款申请")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.overdue
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.compensation
	@pytest.mark.repurchase
	def test_108_loan_pfa(self, r, env, red):
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
				"amount": 33333.33
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
	@pytest.mark.overdue
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.compensation
	@pytest.mark.repurchase
	def test_109_loan_query(self, r, env, red):
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
	@pytest.mark.overdue
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.compensation
	@pytest.mark.repurchase
	def test_110_query_repayment_plan(self, r, env, red):
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
		Assert.check_repayment(False, env, r.get(red["project_id"]))
		r.setex(red["repayment_plan"], 72000, json.dumps(rep['content']['repaymentPlanList']))

	@allure.title("提前结清试算")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_111_calculate(self, r, env, red):
		"""还款计划试算:提前结清"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"transactionId": r.get(red["transaction_id"]),
				"sourceProjectId": r.get(red["source_project_id"]),
				"projectId": r.get(red["project_id"]),
				"businessType": 2,
				"repayTime": Common.get_time("-")
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
	def test_112_calculate(self, r, env, red):
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

	@allure.title("逾期一期")
	@allure.severity(allure.severity_level.BLOCKER)
	@pytest.mark.overdue
	def test_overdue(self, env, r, red):
		"""逾期一期"""
		Universal.overdue(1, env, r.get(red["project_id"]), 1)

	@allure.title("代偿一期")
	@allure.severity(allure.severity_level.BLOCKER)
	@pytest.mark.compensation
	def test_compensation(self, env, r, red):
		"""代偿一期"""
		Universal.compensation(1, env, r.get(red["project_id"]), "jfq")

	@allure.title("回购")
	@allure.severity(allure.severity_level.BLOCKER)
	@pytest.mark.repurchase
	def test_repurchase(self, env, r, red):
		"""回购"""
		Universal.repurchase(1, env, r.get(red["project_id"]), "jfq")

	@allure.title("还款流水推送")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_113_offline_repay_repayment(self, r, env, red):
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
				"transactionId": r.get(red["transaction_id"]),
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

	@allure.title("提前全部结清")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_114_offline_nrepay_early_settlement(self, r, env, red):
		"""线下还款流水推送：提前全部结清"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_plan_date(
			project_id=r.get(red["project_id"]),
			environment=env,
			repayment_plan_type=1,
			period=1
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
				"planPayDate": plan_pay_date['plan_pay_date'],
				"successAmount": success_amount,
				"repayType": 2,
				"period": repayment_plan_list[0]['period'],
				"payTime": "2020-09-18 00:00:00"  # Common.get_time("-")
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

	@pytest.mark.skip("跳过")
	def test_115_debt_transfer(self, r, env, red):
		"""上传债转函"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'kkd_debt_transfer.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get(red["source_user_id"]),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get(red["transaction_id"]),
				"associationId": r.get(red["project_id"])
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

	@allure.title("退货")
	@allure.severity("blocker")
	def test_116_return(self, r, env, red):
		"""退货"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_plan_date(
			project_id=r.get(red["project_id"]),
			environment=env,
			repayment_plan_type=1,
			period=1
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
				"planPayDate": plan_pay_date['plan_pay_date'],
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
		Assert.check_repayment(True, env, r.get(red["project_id"]), param)

	@allure.title("资金流水推送")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_117_capital_flow(self, r, env, red):
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
				"productCode": "FQ_JK_JFQJYV2",
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


if __name__ == '__main__':
	pytest.main()
