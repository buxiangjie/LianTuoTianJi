# -*- coding: UTF-8 -*-
"""
@auth:卜祥杰
@date:2020-05-12 11:26:00
@describe: 卡卡贷12期
"""
import os
import json
import sys
import time
import allure
import pytest

from common.common_func import Common
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@allure.feature("卡卡贷12期")
class TestKkd12Tp:
	file = Config().get_item('File', 'kkd_case_file')

	@allure.title("进件申请")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_100_apply(self, r, env):
		"""进件申请"""
		data = excel_table_byname(self.file, 'apply')
		Common.p2p_get_userinfo('kkd_12_periods', env)
		r.mset(
			{
				"kkd_12_periods_sourceUserId": Common.get_random('userid'),
				"kkd_12_periods_transactionId": Common.get_random('transactionId'),
				"kkd_12_periods_phone": Common.get_random('phone'),
				"kkd_12_periods_sourceProjectId": Common.get_random('sourceProjectId'),
			}
		)
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get('kkd_12_periods_sourceProjectId'),
				"sourceUserId": r.get('kkd_12_periods_sourceUserId'),
				"transactionId": r.get('kkd_12_periods_transactionId')
			}
		)
		param['personalInfo'].update(
			{
				"cardNum": r.get('kkd_12_periods_cardNum'),
				"custName": r.get('kkd_12_periods_custName'),
				"phone": r.get('kkd_12_periods_phone')
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time("-"),
				"productCode": "XJ_WX_KKD",
				"applyTerm": 12
			}
		)
		param['loanInfo'].update({"loanTerm": 12})
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
		r.set('kkd_12_periods_projectId', rep['content']['projectId'])
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("上传进件授信协议")
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_101_sign_credit(self, r, env):
		"""上传进件授信协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'kkd_sign_credit.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('kkd_12_periods_sourceUserId'),
				"contractType": 5,
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get('kkd_12_periods_transactionId'),
				"associationId": r.get('kkd_12_periods_projectId')
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
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_102_query_apply_result(self, r, env):
		"""进件结果查询"""
		GetSqlData.change_project_audit_status(
			project_id=r.get('kkd_12_periods_projectId'),
			environment=env
		)
		data = excel_table_byname(self.file, 'query_apply_result')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get('kkd_12_periods_sourceProjectId'),
				"projectId": r.get('kkd_12_periods_projectId')
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

	@allure.title("上传借款授信协议")
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_103_sign_borrow(self, r, env):
		"""上传借款协议"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'kkd_sign_borrow.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('kkd_12_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get('kkd_12_periods_transactionId'),
				"associationId": r.get('kkd_12_periods_projectId')
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
		r.set("kkd_12_periods_contractId", rep['content']['contractId'])
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("上传担保函")
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_104_sign_guarantee(self, r, env):
		"""上传担保函"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'kkd_sign_guarantee.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('kkd_12_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get('kkd_12_periods_transactionId'),
				"associationId": r.get('kkd_12_periods_projectId')
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

	@allure.title("上传图片")
	@allure.severity("trivial")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	@pytest.mark.skip
	def test_105_image_upload(self, r, env):
		"""上传图片"""
		data = excel_table_byname(self.file, 'image_upload')
		param = json.loads(data[0]['param'])
		param.update({"associationId": r.get('kkd_12_periods_projectId')})
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
	@pytest.mark.offline_settle_in_advance
	def test_106_contact_query(self, r, env):
		"""合同结果查询:获取签章后的借款协议"""
		data = excel_table_byname(self.file, 'contract_query')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"associationId": r.get('kkd_12_periods_projectId'),
				"serviceSn": Common.get_random("serviceSn"),
				"requestTime": Common.get_time("-"),
				"sourceUserId": r.get("kkd_12_periods_sourceUserId"),
				"contractId": r.get("kkd_12_periods_contractId")
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
	@allure.severity("normal")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_107_calculate(self, r, env):
		"""还款计划试算（未放款）:正常还款"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get("kkd_12_periods_sourceUserId"),
				"transactionId": r.get("kkd_12_periods_sourceProjectId"),
				"sourceProjectId": r.get("kkd_12_periods_sourceProjectId"),
				"projectId": r.get("kkd_12_periods_projectId")
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
	@pytest.mark.offline_settle_in_advance
	def test_108_loan_pfa(self, r, env):
		"""放款申请"""
		data = excel_table_byname(self.file, 'loan_pfa')
		param = json.loads(data[0]['param'])
		r.set("kkd_12_periods_loan_serviceSn", Common.get_random("serviceSn"))
		param.update(
			{
				"sourceProjectId": r.get("kkd_12_periods_sourceProjectId"),
				"projectId": r.get("kkd_12_periods_projectId"),
				"sourceUserId": r.get("kkd_12_periods_sourceUserId"),
				"serviceSn": r.get("kkd_12_periods_loan_serviceSn"),
				"id": r.get('kkd_12_periods_cardNum')
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
		time.sleep(8)
		GetSqlData.change_pay_status(
			environment=env,
			project_id=r.get('kkd_12_periods_projectId')
		)

	@allure.title("放款结果查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	@pytest.mark.offline_repay
	@pytest.mark.offline_settle_in_advance
	def test_109_loan_query(self, r, env):
		"""放款结果查询"""
		GetSqlData.loan_set(environment=env, project_id=r.get('kkd_12_periods_projectId'))
		data = excel_table_byname(self.file, 'pfa_query')
		param = json.loads(data[0]['param'])
		param.update({"serviceSn": r.get("kkd_12_periods_loan_serviceSn")})
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
	def test_110_query_repayment_plan(self, r, env):
		"""国投云贷还款计划查询"""
		data = excel_table_byname(self.file, 'query_repayment_plan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"transactionId": r.get("kkd_12_periods_sourceProjectId"),
				"projectId": r.get("kkd_12_periods_projectId")
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
		r.set("kkd_12_periods_repayment_plan", json.dumps(rep['content']['repaymentPlanList']))
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("提前结清试算")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_111_calculate(self, r, env):
		"""还款计划试算:提前结清"""
		data = excel_table_byname(self.file, 'calculate')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get("kkd_12_periods_sourceUserId"),
				"transactionId": r.get("kkd_12_periods_sourceProjectId"),
				"sourceProjectId": r.get("kkd_12_periods_sourceProjectId"),
				"projectId": r.get("kkd_12_periods_projectId"),
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
			"kkd_12_periods_early_settlement_repayment_plan",
			json.dumps(rep['content']['repaymentPlanList'])
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("线下还款流水推送")
	@allure.severity("blocker")
	@pytest.mark.offline_repay
	def test_112_offline_repay_repayment(self, r, env):
		"""线下还款流水推送：正常还一期"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		period = 1
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=r.get("kkd_12_periods_projectId"),
			environment=env,
			period=period,
			repayment_plan_type=1
		)
		repayment_plan_list = r.get("kkd_12_periods_repayment_plan")
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
				"projectId": r.get("kkd_12_periods_projectId"),
				"transactionId": r.get("kkd_12_periods_sourceProjectId"),
				"sourceProjectId": r.get("kkd_12_periods_sourceProjectId"),
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

	@allure.title("提前结清")
	@allure.severity("blocker")
	@pytest.mark.offline_settle_in_advance
	def test_113_offline_repay_early_settlement(self, r, env):
		"""线下还款流水推送：提前全部结清"""
		data = excel_table_byname(self.file, 'offline_repay')
		param = json.loads(data[0]['param'])
		plan_pay_date = GetSqlData.get_repayment_detail(
			project_id=r.get("kkd_12_periods_projectId"),
			environment=env,
			period=1,
			repayment_plan_type=1
		)
		repayment_plan_list = r.get("kkd_12_periods_early_settlement_repayment_plan")
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
				"projectId": r.get("kkd_12_periods_projectId"),
				"transactionId": r.get("kkd_12_periods_sourceProjectId"),
				"sourceProjectId": r.get("kkd_12_periods_sourceProjectId"),
				"sourceRepaymentId": Common.get_random("sourceProjectId"),
				"planPayDate": str(plan_pay_date['plan_pay_date']),
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

	@allure.title("上传债转涵")
	@allure.severity("blocker")
	def test_114_debt_transfer(self, r, env):
		"""上传债转函"""
		data = excel_table_byname(self.file, 'contract_sign')
		param = Common.get_json_data('data', 'kkd_debt_transfer.json')
		param.update(
			{
				"serviceSn": Common.get_random('serviceSn'),
				"sourceUserId": r.get('kkd_12_periods_sourceUserId'),
				"sourceContractId": Common.get_random('userid'),
				"transactionId": r.get('kkd_12_periods_transactionId'),
				"associationId": r.get('kkd_12_periods_projectId')
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
		r.set("kkd_12_periods_contractId", rep['content']['contractId'])
		assert rep['resultCode'] == int(data[0]['resultCode'])


if __name__ == '__main__':
	pytest.main()
