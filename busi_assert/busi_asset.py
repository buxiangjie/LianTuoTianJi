# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 断言
"""
import allure

from assertpy import assert_that
from typing import Optional
from common.get_sql_data import GetSqlData
from busi_assert.info.extra_info import EntityInfo
from log.ulog import Ulog


class Assert:
	@staticmethod
	@allure.step("检查授信/进件字段")
	def check_column(info: str, environment: str, busi_id: str) -> None:
		map_dict = EntityInfo[info].value
		busi_type = info.split("_")[-1]
		sql_data = GetSqlData.select_extra_info(environment, busi_type, busi_id)
		for key, value in map_dict.items():
			Ulog().logger_().info(f"""校验参数:{key}是否落库""")
			assert_that(key in sql_data.keys()).is_true()

	@staticmethod
	@allure.step("检查还款相关表字段")
	def check_repayment(
			is_repay: bool,
			env: str,
			project_id: str,
			param: Optional[dict] = None
	) -> None:
		if is_repay is True:
			if param is None:
				raise OSError("is_repay=True时还款参数不能为空")
			repay_data = Assert._get_repay_data(env, project_id, param)
			if repay_data["repay_type"] == 1:
				Assert._business_type_1_repayment_plan(repay_data)
				Assert._business_type_1_repayment_detail(repay_data)
			elif repay_data["repay_type"] == 2:
				Assert._business_type_2_repayment_plan(repay_data)
				Assert._business_type_2_repayment_detail(repay_data)
			elif repay_data["repay_type"] == 3:
				Assert._business_type_3_repayment_plan(repay_data)
				Assert._business_type_3_repayment_detail(repay_data)
		else:
			Assert._init_repayment_plan(env, project_id)

	@staticmethod
	@allure.step("检查逾期相关表字段")
	def check_overdue(period: int, env: str, project_id: str) -> None:
		"""
		检查逾期后还款计划与资产
		"""
		fee_plan = GetSqlData.get_fee_plan(project_id, env)
		repayment_plan = GetSqlData.get_repayment_plan(project_id=project_id, environment=env)
		_data = {
			"current_fee_plan": [],  # 当前期费计划
			"before_fee_plan": [],  # 已发生的费计划
			"after_fee_plan": [],  # 未发生的费计划
			"current_repayment_plan": [],  # 当前期的还款计划
			"before_repayment_plan": [],  # 已发生的还款计划
			"after_repayment_plan": [],  # 未发生的还款计划
			"asset": GetSqlData.get_asset(project_id, env)
		}
		for f in fee_plan:
			if ["period"] == period:
				_data["current_fee_plan"].append(f)
			elif f["period"] < period:
				_data["before_fee_plan"].append(f)
			else:
				_data["after_fee_plan"].append(f)
		for p in repayment_plan:
			if p["period"] == period:
				_data["current_repayment_plan"].append(p)
			elif p["period"] < period:
				_data["before_repayment_plan"].append(p)
			else:
				_data["after_repayment_plan"].append(p)
		if len(fee_plan) == 0:
			Ulog().logger_().info("无费计划,不需要校验")
		else:
			for fee in _data["current_fee_plan"]:
				assert_that(fee["overdue_status"]).is_equal_to(1)
				assert_that(fee["overdue_days"]).is_greater_than(0)
			Ulog().logger_().info("费计划逾期状态与逾期天数校验通过")
		for plan in _data["current_repayment_plan"]:
			assert_that(plan["overdue_status"]).is_equal_to(1)
			assert_that(plan["overdue_days"]).is_greater_than(0)
		Ulog().logger_().info("还款计划逾期状态与逾期天数校验通过")
		assert_that(_data["asset"]["cur_overdue_days"]).is_greater_than(0)
		Ulog().logger_().info("资产当前逾期天数校验通过")

	@staticmethod
	@allure.step("检查债转相关表字段")
	def check_swap(
			period: int,
			env: str,
			project_id: str,
			is_compensation: Optional[bool] = True
	) -> None:
		swap_data = Assert._get_swap_data(env, project_id, period)
		if is_compensation:
			Assert._compensation_assert(swap_data)
		else:
			Assert._repurchase_assert(swap_data)

	@staticmethod
	def _get_repay_data(env: str, project_id: str, param: Optional[dict]) -> dict:
		"""
		初始化校验需要用到的还款数据
		:param env:
		:param project_id:
		:param param:
		:return:
		"""
		_data = {
			"repay_type": param["repayType"],
			"period": param["period"],
			"pay_time": param["payTime"],
			"repayment_detail": param["repaymentDetailList"],
			"repay_principal": 0,
			"repay_interest": 0,
			"plan_pay_date": None,
			"success_amount": param["successAmount"],
			"payment_flow_source": param["paymentFlowSource"],
			"source_repayment_id": param["sourceRepaymentId"],
			"maturity": GetSqlData.get_maturity(project_id=project_id, environment=env),
			"database_repayment_plan": GetSqlData.get_repayment_plan(project_id=project_id, environment=env),
			"database_fee_plan": GetSqlData.get_fee_plan(project_id, env),
			"database_repayment": GetSqlData.get_repayment(project_id, env)[-1],
			"database_repayment_detail": GetSqlData.get_repayment_detail(project_id, env),
			"current_repayment_plan": [],  # 当前期的还款计划
			"before_repayment_plan": [],  # 已发生的还款计划
			"after_repayment_plan": [],  # 未发生的还款计划
			"current_fee_plan": [],  # 当前期费计划
			"before_fee_plan": [],  # 已发生的费计划
			"after_fee_plan": [],  # 未发生的费计划
			"current_repayment_detail": [],  # 当前期还款流水
			"before_repayment_detail": [],  # 已发生的还款流水
			"after_repayment_detail": []  # 未发生的还款流水
		}
		_data["plan_pay_date"] = GetSqlData.get_repayment_plan_date(project_id, env, 1, _data["period"])[
			"plan_pay_date"]
		for p in _data["database_repayment_plan"]:
			if p["period"] == _data["period"]:
				_data["current_repayment_plan"].append(p)
			elif p["period"] < _data["period"]:
				_data["before_repayment_plan"].append(p)
			else:
				_data["after_repayment_plan"].append(p)
		for f in _data["database_fee_plan"]:
			if f["period"] == _data["period"]:
				_data["current_fee_plan"].append(f)
			elif f["period"] < _data["period"]:
				_data["before_fee_plan"].append(f)
			else:
				_data["after_fee_plan"].append(f)
		for detail in _data["repayment_detail"]:
			if detail["planCategory"] == 1:
				_data["repay_principal"] += detail["payAmount"]
			elif detail["planCategory"] == 2:
				_data["repay_interest"] += detail["payAmount"]
		for repayment_detail in _data["database_repayment_detail"]:
			if repayment_detail["period"] < _data["period"]:
				_data["before_repayment_detail"].append(repayment_detail)
			elif repayment_detail["period"] == _data["period"]:
				_data["current_repayment_detail"].append(repayment_detail)
			elif repayment_detail["period"] > _data["period"]:
				_data["after_repayment_detail"].append(repayment_detail)
		return _data

	@staticmethod
	def _get_swap_data(env: str, project_id: str, period: int):
		_data = {
			"period": period,
			"current_repayment_plan": [],  # 当前期的还款计划
			"before_repayment_plan": [],  # 已发生的还款计划
			"after_repayment_plan": [],  # 未发生的还款计划
			"current_fee_plan": [],  # 当前期费计划
			"before_fee_plan": [],  # 已发生的费计划
			"after_fee_plan": [],  # 未发生的费计划
			"current_swap_detail": [],  # 当前期债转详情
			"before_swap_detail": [],  # 已发生期的债转详情
			"after_swap_detail": [],  # 未发生期的债转详情
			"maturity": GetSqlData.get_maturity(project_id=project_id, environment=env),
			"database_repayment_plan": GetSqlData.get_repayment_plan(project_id=project_id, environment=env),
			"database_fee_plan": GetSqlData.get_fee_plan(project_id, env),
			"database_swap_detail": GetSqlData.get_swap_detail(project_id,env),
			"asset": GetSqlData.get_asset(project_id, env)
		}
		for p in _data["database_repayment_plan"]:
			if p["period"] == period:
				_data["current_repayment_plan"].append(p)
			elif p["period"] < period:
				_data["before_repayment_plan"].append(p)
			else:
				_data["after_repayment_plan"].append(p)
		for f in _data["database_fee_plan"]:
			if f["period"] == period:
				_data["current_fee_plan"].append(f)
			elif f["period"] < period:
				_data["before_fee_plan"].append(f)
			else:
				_data["after_fee_plan"].append(f)
		for s in _data["database_swap_detail"]:
			if s["period"] == period:
				_data["current_swap_detail"].append(s)
			elif s["period"] < period:
				_data["before_swap_detail"].append(s)
			else:
				_data["after_swap_detail"].append(s)
		return _data

	@staticmethod
	def _compensation_assert(swap_data: dict) -> None:
		"""
		代偿检查
		:param swap_data:
		:return:
		"""
		if len(swap_data["current_fee_plan"]) > 0:
			for fee in swap_data["current_fee_plan"]:
				assert_that(fee["credit_assign_method"]).is_equal_to(2)
				assert_that(fee["current_vendor"]).is_not_equal_to(1)
				assert_that(fee["current_channel"]).is_not_equal_to(1)
			Ulog().logger_().info("费计划的归属/当前所属渠道校验通过")
		else:
			assert_that(swap_data["current_swap_detail"]).is_length(2)
			Ulog().logger_().info("债转详情条数校验通过")
		Ulog().logger_().info("还款计划的归属/当前所属渠道校验通过")
		if swap_data["period"] == swap_data["maturity"]:
			assert_that(swap_data["asset"]["current_vendor"]).is_not_equal_to(1)
			assert_that(swap_data["asset"]["current_channel"]).is_not_equal_to(1)
			Ulog().logger_().info("资产表当前归属渠道校验通过")
		for swap_detail in swap_data["current_swap_detail"]:
			for repayment_plan in swap_data["current_repayment_plan"]:
				assert_that(repayment_plan["credit_assign_method"]).is_equal_to(2)
				assert_that(repayment_plan["current_vendor"]).is_not_equal_to(1)
				assert_that(repayment_plan["current_channel"]).is_not_equal_to(1)
				if swap_detail["repayment_plan_type"] == repayment_plan["repayment_plan_type"]:
					assert_that(swap_detail["action_amount"]).is_equal_to(repayment_plan["cur_amount"])
					assert_that(swap_detail["credit_assign_method"]).is_equal_to(repayment_plan["credit_assign_method"])
					assert_that(swap_detail["current_vendor"]).is_equal_to(repayment_plan["current_vendor"])
					assert_that(swap_detail["current_channel"]).is_equal_to(repayment_plan["current_channel"])
		Ulog().logger_().info("还款计划所属渠道校验通过")
		Ulog().logger_().info("债转详情转移金额/所属渠道校验通过")

	@staticmethod
	def _repurchase_assert(swap_data: dict) -> None:
		"""
		回购检查
		:param swap_data:
		:return:
		"""
		Assert._compensation_assert(swap_data)
		if len(swap_data["after_fee_plan"]) > 0:
			for fee in swap_data["after_fee_plan"]:
				if fee["period"] < swap_data["period"] + 2:
					assert_that(fee["credit_assign_method"]).is_equal_to(2)
				else:
					assert_that(fee["credit_assign_method"]).is_equal_to(3)
				assert_that(fee["current_vendor"]).is_not_equal_to(1)
				assert_that(fee["current_channel"]).is_not_equal_to(1)
			Ulog().logger_().info("未发生期费计划的归属/当前所属渠道校验通过")
		for repayment_plan in swap_data["after_repayment_plan"]:
			if repayment_plan["period"] < swap_data["period"] + 2:
				assert_that(repayment_plan["credit_assign_method"]).is_equal_to(2)
			else:
				assert_that(repayment_plan["credit_assign_method"]).is_equal_to(3)
			assert_that(repayment_plan["current_vendor"]).is_not_equal_to(1)
			assert_that(repayment_plan["current_channel"]).is_not_equal_to(1)
		Ulog().logger_().info("未发生期还款计划所属渠道校验通过")
		swap_detail_count = 0
		for swap_detail in swap_data["after_swap_detail"]:
			if swap_detail["period"] < swap_data["period"] + 2:
				assert_that(swap_detail["credit_assign_method"]).is_equal_to(2)
			else:
				assert_that(swap_detail["credit_assign_method"]).is_not_equal_to(2)
				assert_that(swap_detail["plan_category"]).is_equal_to(1)
				swap_detail_count += 1
		Ulog().logger_().info("未发生期回购流水所属渠道/流水类型校验通过")
		assert_that(swap_detail_count).is_equal_to(swap_data["maturity"] - (swap_data["period"] + 1))
		Ulog().logger_().info("回购期回购流水条数校验通过")
		assert_that(swap_data["asset"]["current_vendor"]).is_not_equal_to(1)
		assert_that(swap_data["asset"]["current_channel"]).is_not_equal_to(1)
		Ulog().logger_().info("资产表当前归属渠道校验通过")

	@staticmethod
	def _business_type_1_repayment_detail(repay_data: dict) -> None:
		assert_that(repay_data["database_repayment"]["repay_type"]).is_equal_to(1)
		assert_that(repay_data["database_repayment"]["success_amount"]).is_equal_to(repay_data["success_amount"])
		assert_that(repay_data["database_repayment"]["funding_source"]).is_equal_to(repay_data["payment_flow_source"])
		assert_that(repay_data["database_repayment"]["pay_time"]).is_equal_to(repay_data["pay_time"])
		assert_that(repay_data["database_repayment"]["source_repayment_id"]).is_equal_to(
			repay_data["source_repayment_id"])
		Ulog().logger_().info(f"第{repay_data['period']}期repayment表还款类型/成功金额/资金来源/还款时间/渠道还款ID校验通过")
		if len(repay_data["current_fee_plan"]) == 0:
			Ulog().logger_().info("当前期无费计划,无需校验")
		else:
			fee_detail_count = 0
			not_fee_detail_count = 0
			Ulog().logger_().info("开始校验费计划与费流水")
			for fee_plan in repay_data["current_fee_plan"]:
				for fee_detail in repay_data["current_repayment_detail"]:
					if fee_plan["fee_category"] == fee_detail["plan_category"]:
						fee_detail_count += 1
						assert_that(fee_detail["repayment_plan_type"]).is_equal_to(3)
						assert_that(fee_detail["credit_assign_method"]).is_equal_to(fee_plan["credit_assign_method"])
						assert_that(fee_detail["pay_time"]).is_equal_to(repay_data["pay_time"])
						assert_that(fee_detail["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
						assert_that(fee_plan["fee_status"]).is_equal_to(3)
						assert_that(fee_plan["rest_amount"]).is_equal_to(0)
						assert_that(fee_plan["pay_time"]).is_equal_to(repay_data["pay_time"])
			if fee_detail_count == 0:
				Ulog().logger_().error("费计划与费流水不匹配")
			Ulog().logger_().info("费计划/费流水的还款类型/资金归属/还款时间/计划还款时间/费状态/剩余应还金额校验通过")
			for repayment_plan in repay_data["current_repayment_plan"]:
				for repayment_detail in repay_data["current_repayment_detail"]:
					if repayment_plan["repayment_plan_type"] == repayment_detail["plan_category"]:
						not_fee_detail_count += 1
						assert_that(repayment_detail["pay_time"]).is_equal_to(repay_data["pay_time"])
						assert_that(repayment_detail["this_pay_amount"]).is_equal_to(repayment_plan["pay_amount"])
			if not_fee_detail_count == 0:
				Ulog().logger_().error("还款计划与还款流水不匹配")
			Ulog().logger_().info("还款流水的还款时间/还款金额校验通过")

	@staticmethod
	def _business_type_2_repayment_detail(repay_data: dict) -> None:
		assert_that(repay_data["database_repayment"]["repay_type"]).is_equal_to(2)
		assert_that(repay_data["database_repayment"]["success_amount"]).is_equal_to(repay_data["success_amount"])
		assert_that(repay_data["database_repayment"]["funding_source"]).is_equal_to(repay_data["payment_flow_source"])
		assert_that(repay_data["database_repayment"]["pay_time"]).is_equal_to(repay_data["pay_time"])
		assert_that(repay_data["database_repayment"]["source_repayment_id"]).is_equal_to(
			repay_data["source_repayment_id"])
		Ulog().logger_().info(f"第{repay_data['period']}期提前结清repayment表还款类型/成功金额/资金来源/还款时间/渠道还款ID校验通过")
		if len(repay_data["current_fee_plan"]) == 0:
			Ulog().logger_().info("当前期无费计划,无需校验")
		else:
			fee_detail_count = 0
			not_fee_detail_count = 0
			Ulog().logger_().info("开始校验费计划与费流水")
			for fee_plan in repay_data["current_fee_plan"]:
				if fee_plan["fee_status"] == 3:
					for fee_detail in repay_data["current_repayment_detail"]:
						if fee_plan["fee_category"] == fee_detail["plan_category"]:
							fee_detail_count += 1
							assert_that(fee_detail["repayment_plan_type"]).is_equal_to(3)
							assert_that(fee_detail["credit_assign_method"]).is_equal_to(
								fee_plan["credit_assign_method"])
							assert_that(fee_detail["pay_time"]).is_equal_to(repay_data["pay_time"])
							assert_that(fee_detail["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
							assert_that(fee_plan["fee_status"]).is_equal_to(3)
							assert_that(fee_plan["rest_amount"]).is_equal_to(0)
							assert_that(fee_plan["pay_time"]).is_equal_to(repay_data["pay_time"])
			is_9001 = False
			for fee in repay_data["current_fee_plan"]:
				if fee["fee_category"] == 9001:
					is_9001 = True
			if is_9001 is True:
				assert_that(repay_data["after_fee_plan"]).is_length(repay_data["maturity"] - repay_data["period"])
			if fee_detail_count == 0:
				raise AssertionError("费计划与费流水不匹配")
			Ulog().logger_().info("费计划/费流水的还款类型/资金归属/还款时间/计划还款时间/费状态/剩余应还金额校验通过")
			for repayment_plan in repay_data["current_repayment_plan"]:
				if repayment_plan["repayment_status"] == 3:
					for repayment_detail in repay_data["current_repayment_detail"]:
						if repayment_plan["repayment_plan_type"] == repayment_detail["plan_category"]:
							not_fee_detail_count += 1
							assert_that(repayment_detail["pay_time"]).is_equal_to(repay_data["pay_time"])
							assert_that(repayment_detail["this_pay_amount"]).is_equal_to(repayment_plan["pay_amount"])
			if not_fee_detail_count == 0:
				raise AssertionError("还款计划与还款流水不匹配")
			Ulog().logger_().info("还款流水的还款时间/还款金额校验通过")

	@staticmethod
	def _business_type_3_repayment_detail(repay_data: dict) -> None:
		assert_that(repay_data["database_repayment"]["repay_type"]).is_equal_to(3)
		assert_that(repay_data["database_repayment"]["success_amount"]).is_equal_to(repay_data["success_amount"])
		assert_that(repay_data["database_repayment"]["funding_source"]).is_equal_to(repay_data["payment_flow_source"])
		assert_that(repay_data["database_repayment"]["pay_time"]).is_equal_to(repay_data["pay_time"])
		assert_that(repay_data["database_repayment"]["source_repayment_id"]).is_equal_to(
			repay_data["source_repayment_id"])
		Ulog().logger_().info(f"第{repay_data['period']}期提前结清repayment表还款类型/成功金额/资金来源/还款时间/渠道还款ID校验通过")
		if len(repay_data["current_fee_plan"]) == 0:
			Ulog().logger_().info("当前期无费计划,无需校验")
		else:
			fee_detail_count = 0
			not_fee_detail_count = 0
			Ulog().logger_().info("开始校验费计划与费流水")
			for fee_plan in repay_data["current_fee_plan"]:
				if fee_plan["fee_status"] == 3:
					for fee_detail in repay_data["current_repayment_detail"]:
						if fee_plan["fee_category"] == fee_detail["plan_category"]:
							fee_detail_count += 1
							assert_that(fee_detail["repayment_plan_type"]).is_equal_to(3)
							assert_that(fee_detail["credit_assign_method"]).is_equal_to(
								fee_plan["credit_assign_method"])
							assert_that(fee_detail["pay_time"]).is_equal_to(repay_data["pay_time"])
							assert_that(fee_detail["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
							assert_that(fee_plan["fee_status"]).is_equal_to(3)
							assert_that(fee_plan["rest_amount"]).is_equal_to(0)
							assert_that(fee_plan["pay_time"]).is_equal_to(repay_data["pay_time"])
			is_9001 = False
			for fee in repay_data["current_fee_plan"]:
				if fee["fee_category"] == 9001:
					is_9001 = True
			if is_9001 is True:
				assert_that(repay_data["after_fee_plan"]).is_length(repay_data["maturity"] - repay_data["period"])
			if fee_detail_count == 0:
				raise AssertionError("费计划与费流水不匹配")
			Ulog().logger_().info("费计划/费流水的还款类型/资金归属/还款时间/计划还款时间/费状态/剩余应还金额校验通过")
			for repayment_plan in repay_data["current_repayment_plan"]:
				if repayment_plan["repayment_status"] == 3:
					for repayment_detail in repay_data["current_repayment_detail"]:
						if repayment_plan["repayment_plan_type"] == repayment_detail["plan_category"]:
							not_fee_detail_count += 1
							assert_that(repayment_detail["pay_time"]).is_equal_to(repay_data["pay_time"])
							assert_that(repayment_detail["this_pay_amount"]).is_equal_to(repayment_plan["pay_amount"])
			if not_fee_detail_count == 0:
				raise AssertionError("还款计划与还款流水不匹配")
			Ulog().logger_().info("还款流水的还款时间/还款金额校验通过")

	@staticmethod
	def _business_type_1_repayment_plan(repay_data: dict) -> None:
		"""
		还款类型为1时的还款计划校验
		:param repay_data:
		:return:
		"""
		Ulog().logger_().info("业务类型为正常还款")
		# 校验当前期还款计划条数是否正确
		assert_that(repay_data["current_repayment_plan"]).is_length(2)
		Ulog().logger_().info("当前期还款计划条数校验成功")
		for current in repay_data["current_repayment_plan"]:
			# 校验还款计划的计划应还时间是否正确
			assert_that(current["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
			if current["repayment_plan_type"] == 1:
				Ulog().logger_().info(f"第{current['period']}期本金还款计划应还时间校验通过")
			else:
				Ulog().logger_().info(f"第{current['period']}期利息还款计划应还时间校验通过")
			assert_that(current["business_type"]).is_equal_to(1)
			# 校验每一条还款计划的实际还款时间是否一致
			assert_that(current["pay_time"]).is_equal_to(repay_data["pay_time"])
			if current["repayment_plan_type"] == 1:
				Ulog().logger_().info(f"第{current['period']}期本金还款计划实还时间校验通过")
			else:
				Ulog().logger_().info(f"第{current['period']}期利息还款计划实还时间校验通过")
			# 校验每一条还款计划的实际还款金额是否一致
			assert_that(current["pay_amount"]).is_equal_to(current["cur_amount"])
			if current["repayment_plan_type"] == 1:
				Ulog().logger_().info(f"第{current['period']}期本金还款计划实还金额校验通过")
			else:
				Ulog().logger_().info(f"第{current['period']}期利息还款计划实还金额校验通过")
			# 校验每一条还款计划的实际还款金额是否为0
			assert_that(current["rest_amount"]).is_equal_to(0.0)
			if current["repayment_plan_type"] == 1:
				Ulog().logger_().info(f"第{current['period']}期本金还款计划剩余应还金额校验通过")
			else:
				Ulog().logger_().info(f"第{current['period']}期利息还款计划剩余应还金额校验通过")

	@staticmethod
	def _business_type_2_repayment_plan(repay_data: dict) -> None:
		"""
		还款类型为2时的还款计划校验
		:param repay_data:
		:return:
		"""
		Ulog().logger_().info("业务类型为提前结清")
		assert_that(repay_data["current_repayment_plan"]).is_length(4)
		status_9, status_3 = 0, 0
		for current in repay_data["current_repayment_plan"]:
			principal = 0
			interest = 0
			for ori in repay_data["current_repayment_plan"]:
				if ori["repayment_plan_type"] == 1 and ori["repayment_status"] == 3:
					principal = ori["origin_amount"]
				elif ori["repayment_plan_type"] == 2 and ori["repayment_status"] == 3:
					interest = ori["origin_amount"]
			if current["repayment_status"] == 3:
				status_3 += 1
				if current["repayment_plan_type"] == 1:
					assert_that(current["cur_amount"]).is_equal_to(repay_data["repay_principal"])
					assert_that(current["pay_amount"]).is_equal_to(repay_data["repay_principal"])
					assert_that(current["origin_amount"]).is_equal_to(principal)
					assert_that(current["pay_time"]).is_equal_to(repay_data["pay_time"])
					assert_that(current["rest_amount"]).is_equal_to(0)
					assert_that(current["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
					Ulog().logger_().info("当前期新生成本金剩余应还金额/实际应还金额/原始应还金额/计划还款时间校验通过")
				else:
					assert_that(current["cur_amount"]).is_equal_to(repay_data["repay_interest"])
					assert_that(current["pay_amount"]).is_equal_to(repay_data["repay_interest"])
					assert_that(current["origin_amount"]).is_equal_to(interest)
					assert_that(current["pay_time"]).is_equal_to(repay_data["pay_time"])
					assert_that(current["rest_amount"]).is_equal_to(0)
					assert_that(current["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
					Ulog().logger_().info("当前期新生成利息剩余应还金额/实际应还金额/原始应还金额/计划还款时间校验通过")
			elif current["repayment_status"] == 9:
				status_9 += 1
				assert_that(current["cur_amount"]).is_equal_to(current["origin_amount"])
				assert_that(current["pay_amount"]).is_equal_to(0)
				Ulog().logger_().info("当前期已取消还款计划的当前应还金额/实还金额是否通过")
			assert_that(current["business_type"]).is_equal_to(2)
			Ulog().logger_().info("当前期的业务类型是否通过")
		assert_that(status_9).is_equal_to(2)
		assert_that(status_3).is_equal_to(2)
		Ulog().logger_().info("当前期还款计划条数校验通过")
		for before in repay_data["before_repayment_plan"]:
			assert_that(before["repayment_status"]).is_equal_to(3)
			assert_that(before["business_type"]).is_equal_to(1)
		assert_that(repay_data["before_repayment_plan"]).is_length((repay_data["period"] - 1) * 2)
		Ulog().logger_().info("已发生期还款计划条数/状态校验通过")
		for after in repay_data["after_repayment_plan"]:
			assert_that(after["repayment_status"]).is_equal_to(9)
			assert_that(after["business_type"]).is_equal_to(2)
		assert_that(repay_data["after_repayment_plan"]).is_length(
			(repay_data["maturity"] - repay_data["period"]) * 2)
		Ulog().logger_().info("未发生期还款计划条数/状态校验通过")

	@staticmethod
	def _business_type_3_repayment_plan(repay_data: dict) -> None:
		"""
		还款类型为3时的还款计划校验
		:param repay_data:
		:return:
		"""
		Ulog().logger_().info("业务类型为退货")
		assert_that(repay_data["current_repayment_plan"]).is_length(4)
		status_9, status_3 = 0, 0
		for current in repay_data["current_repayment_plan"]:
			principal = 0
			interest = 0
			for ori in repay_data["current_repayment_plan"]:
				if ori["repayment_plan_type"] == 1 and ori["repayment_status"] == 3:
					principal = ori["origin_amount"]
				elif ori["repayment_plan_type"] == 2 and ori["repayment_status"] == 3:
					interest = ori["origin_amount"]
			if current["repayment_status"] == 3:
				status_3 += 1
				if current["repayment_plan_type"] == 1:
					assert_that(current["cur_amount"]).is_equal_to(repay_data["repay_principal"])
					assert_that(current["pay_amount"]).is_equal_to(repay_data["repay_principal"])
					assert_that(current["origin_amount"]).is_equal_to(principal)
					assert_that(current["pay_time"]).is_equal_to(repay_data["pay_time"])
					assert_that(current["rest_amount"]).is_equal_to(0)
					assert_that(current["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
					Ulog().logger_().info("当前期本金剩余应还金额/实际应还金额/原始应还金额/计划还款时间校验通过")
				else:
					assert_that(current["cur_amount"]).is_equal_to(repay_data["repay_interest"])
					assert_that(current["pay_amount"]).is_equal_to(repay_data["repay_interest"])
					assert_that(current["origin_amount"]).is_equal_to(interest)
					assert_that(current["pay_time"]).is_equal_to(repay_data["pay_time"])
					assert_that(current["rest_amount"]).is_equal_to(0)
					assert_that(current["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
					Ulog().logger_().info("当前期本金剩余应还金额/实际应还金额/原始应还金额/计划还款时间校验通过")
			elif current["repayment_status"] == 9:
				status_9 += 1
				assert_that(current["cur_amount"]).is_equal_to(current["origin_amount"])
				assert_that(current["pay_amount"]).is_equal_to(0)
				if current["repayment_plan_type"] == 1:
					Ulog().logger_().info("当前期已取消本金还款计划的当前应还金额/实还金额校验通过")
				else:
					Ulog().logger_().info("当前期已取消利息还款计划的当前应还金额/实还金额校验通过")
			assert_that(current["business_type"]).is_equal_to(3)
			Ulog().logger_().info("当前期的业务类型校验通过")
		assert_that(status_9).is_equal_to(2)
		assert_that(status_3).is_equal_to(2)
		Ulog().logger_().info("当前期还款计划条数校验通过")

	@staticmethod
	def _init_repayment_plan(env: str, project_id: str) -> None:
		"""
		放款时还款计划校验
		:param env:
		:param project_id:
		:return:
		"""
		database_repayment_plan = GetSqlData.get_repayment_plan(project_id=project_id, environment=env)
		maturity = GetSqlData.get_maturity(project_id=project_id, environment=env)
		for plan in database_repayment_plan:
			assert_that(plan["repayment_status"]).is_equal_to(1)
		Ulog().logger_().info("还款计划状态校验通过")
		assert_that(database_repayment_plan).is_length(maturity * 2)
		Ulog().logger_().info("还款计划条数校验通过")
