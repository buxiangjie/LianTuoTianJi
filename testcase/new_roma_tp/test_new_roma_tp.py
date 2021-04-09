#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2020.02.15 15:25
@describe:新罗马车贷业务流程接口
"""

import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import allure
import pytest
from common.common_func import Common
from common.open_excel import excel_table_byname
from config.configer import Config
from common.get_sql_data import GetSqlData


@allure.feature("新罗马车贷")
class TestNewRomaTp:
	file = Config().get_item('File', 'new_roma_case_file')

	@allure.title("额度授信")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	def test_100_credit_apply(self, r, env, red):
		"""额度授信"""
		data = excel_table_byname(self.file, 'credit_apply_data_new')
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
		param['riskSuggestion'].update(
			{
				"firstCreditDate": Common.get_new_time("before", "days", 30)
			}
		)
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"serviceSn": Common.get_random('serviceSn'),
				"transactionId": r.get(red["transaction_id"])
			}
		)
		param['orderDetail']['employeeNum'] = 10
		param['phoneInfoList'][0].update(
			{
				"isSelf": "Y",
				"phoneStatus": 1,
				"timeLength": 24
			}
		)
		# param['applyInfo']['productCode'] = 'XJ_ROMA_CAR'
		if len(data[0]['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data[0]['headers'])
		rep = Common.response(
			faceaddr=data[0]['url'], headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=env
		)
		assert rep['resultCode'] == int(data[0]['resultCode'])
		r.setex(red["credit_id"], 72000, rep['content']['creditId'])
		r.setex(red["user_id"], 72000, rep['content']['userId'])

	@allure.title("图片上传")
	@allure.severity("normal")
	@pytest.mark.asset
	def test_101_upload_image(self, r, env, red):
		"""图片上传：授信"""
		data = excel_table_byname(self.file, 'image_upload')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"associationId": r.get(red["credit_id"]),
				"bizType": 1
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

	@allure.title("上传授信协议")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	def test_1011_sign_credit(self, r, env, red):
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
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("授信结果查询")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	def test_102_query_result(self, r, env, red):
		"""授信结果查询"""
		GetSqlData.credit_set(environment=env, credit_id=r.get(red["credit_id"]))
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
		assert rep['resultCode'] == int(data[0]['resultCode'])

	@allure.title("用户额度查询")
	@allure.severity("normal")
	@pytest.mark.project
	@pytest.mark.asset
	def test_103_query_user_amount(self, r, env, red):
		"""用户额度查询"""
		data = excel_table_byname(self.file, 'query_user_amount')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceUserId": r.get(red["source_user_id"]),
				"userId": r.get(red["user_id"]),
				# "productCode": "XJ_ROMA_CAR"
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

	@allure.title("进件申请")
	@allure.severity("blocker")
	@pytest.mark.project
	@pytest.mark.asset
	def test_104_project_apply(self, r, env, red):
		"""进件"""
		data = excel_table_byname(self.file, 'test_project')
		param = json.loads(data[0]['param'])
		r.set(red["source_project_id"], Common.get_random('sourceProjectId'))
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
				"phone": r.get(red["phone"]),
				"hasChildren": "Y"
			}
		)
		param['applyInfo'].update(
			{
				"applyTime": Common.get_time(),
				# "productCode": "XJ_ROMA_CAR"
			}
		)
		param['riskSuggestion'].update(
			{
				"firstCreditDate": r.get(red["first_credit_date"])
			}
		)
		param['cardInfo'].update(
			{
				"bankNameSub": "建设银行",
				"bankCode": "34",
				"bankCardNo": "6227002432220410613"
			}
		)
		param['extraInfo']['vin'] = Common.get_random("businessLicenseNo")
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
	def test_105_query_apply_result(self, r, env, red):
		"""进件结果查询"""
		data = excel_table_byname(self.file, 'project_query_apply_result')
		GetSqlData.change_project_audit_status(
			project_id=r.get(red["project_id"]),
			environment=env
		)
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
		assert rep['content']['auditStatus'] == 2

	@allure.title("上传借款合同")
	@allure.severity("blocker")
	@pytest.mark.asset
	def test_106_contract_sign(self, r, env, red):
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

	@allure.title("申请放款")
	@allure.severity("blocker")
	@pytest.mark.asset
	def test_107_pfa(self, r, env, red):
		"""放款"""
		data = excel_table_byname(self.file, 'project_loan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"sourceProjectId": r.get(red["source_project_id"]),
				"projectId": r.get(red["project_id"]),
				"sourceUserId": r.get(red["source_user_id"]),
				"serviceSn": Common.get_random('serviceSn'),
				"accountName": r.get(red["user_name"]),
				"id": r.get(red["id_card"]),
				"bankCode": "CCB",
				"accountNo": "6227002432220410613"  # 6227003814170172872
			}
		)
		r.set(red["loan_service_sn"], param['serviceSn'])
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
		# 修改支付表中的品钛返回code
		GetSqlData.change_pay_status(
			environment=env,
			project_id=r.get(red["project_id"])
		)

	@allure.title("放款结果查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	def test_108_query(self, r, env, red):
		"""放款结果查询"""
		GetSqlData.loan_set(environment=env, project_id=r.get(red["project_id"]))
		data = excel_table_byname(self.file, 'query')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"serviceSn": r.get(red["loan_service_sn"])
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

	@allure.title("还款计划查询")
	@allure.severity("blocker")
	@pytest.mark.asset
	def test_109_query_repayment_plan(self, r, env, red):
		"""还款计划查询"""
		data = excel_table_byname(self.file, 'query_repayment_plan')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"transactionId": Common.get_random("transactionId"),
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

	@allure.title("还款计划试算")
	@allure.severity("blocker")
	@pytest.mark.asset
	def test_110_pre_clear_calculate(self, r, env, red):
		"""还款计划试算"""
		data = excel_table_byname(self.file, 'calculate')
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

	@pytest.mark.skip
	def test_111_offline_partial(self, r, env, red):
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
				"successAmount": 76,
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

	@pytest.mark.skip
	def test_112_push_reconciliation_result(self, r, env, red):
		"""对账结果推送"""
		data = excel_table_byname(self.file, 'push_reconciliation_result')
		param = json.loads(data[0]['param'])
		param.update(
			{
				"accountId": Common.get_random("transactionId")
			}
		)
		for i in param['resultList']:
			i['businessDate'] = Common.get_time('day')
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


if __name__ == '__main__':
	pytest.main()
