# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 断言
"""
from assertpy import assert_that
from typing import Optional
from common.get_sql_data import GetSqlData
from busi_assert.info.extra_info import EntityInfo
from log.ulog import Ulog


class Assert:
	@staticmethod
	def check_column(info: str, environment: str, busi_id: str) -> None:
		map_dict = EntityInfo[info].value
		busi_type = info.split("_")[-1]
		sql_data = GetSqlData.select_extra_info(environment, busi_type, busi_id)
		for key, value in map_dict.items():
			Ulog.info(f"""校验参数:{key}是否落库""")
			assert_that(key in sql_data.keys()).is_true()

	@staticmethod
	def check_repayment_plan(is_repay: bool, env: str, project_id: str, param: Optional[dict]) -> None:
		if is_repay is True:
			repay_data = Assert._get_repay_data(env, project_id, param)
			if repay_data["repay_type"] == 1:
				Assert._business_type_1_repayment_plan(repay_data)
			elif repay_data["repay_type"] == 2:
				Assert._business_type_2_repayment_plan(repay_data)
			elif repay_data["repay_type"] == 3:
				Assert._business_type_3_repayment_plan(repay_data)

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
			"maturity": GetSqlData.get_maturity(project_id=project_id, environment=env),
			"database_repayment_plan": GetSqlData.get_repayment_plan(project_id=project_id, environment=env),
			"current_repayment_plan": [],  # 当前期的还款计划
			"before_repayment_plan": [],  # 已发生的还款计划
			"after_repayment_plan": [],  # 未发生的还款计划
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
		for detail in _data["repayment_detail"]:
			if detail["planCategory"] == 1:
				_data["repay_principal"] += detail["payAmount"]
			elif detail["planCategory"] == 2:
				_data["repay_interest"] += detail["payAmount"]
		return _data

	@staticmethod
	def _business_type_1_repayment_plan(repay_data: dict) -> None:
		"""
		还款类型为1时的还款计划校验
		:param repay_data:
		:return:
		"""
		Ulog.info("业务类型为正常还款")
		# 校验当前期还款计划条数是否正确
		assert_that(repay_data["current_repayment_plan"]).is_length(2)
		Ulog.info("当前期还款计划条数校验成功")
		for current in repay_data["current_repayment_plan"]:
			# 校验还款计划的计划应还时间是否正确
			assert_that(current["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
			if current["repayment_plan_type"] == 1:
				Ulog.info(f"第{current['period']}期本金还款计划应还时间校验通过")
			else:
				Ulog.info(f"第{current['period']}期利息还款计划应还时间校验通过")
			assert_that(current["business_type"]).is_equal_to(1)
			# 校验每一条还款计划的实际还款时间是否一致
			assert_that(current["pay_time"]).is_equal_to(repay_data["pay_time"])
			if current["repayment_plan_type"] == 1:
				Ulog.info(f"第{current['period']}期本金还款计划实还时间校验通过")
			else:
				Ulog.info(f"第{current['period']}期利息还款计划实还时间校验通过")
			# 校验每一条还款计划的实际还款金额是否一致
			assert_that(current["pay_amount"]).is_equal_to(current["cur_amount"])
			if current["repayment_plan_type"] == 1:
				Ulog.info(f"第{current['period']}期本金还款计划实还金额校验通过")
			else:
				Ulog.info(f"第{current['period']}期利息还款计划实还金额校验通过")
			# 校验每一条还款计划的实际还款金额是否为0
			assert_that(current["rest_amount"]).is_equal_to(0.0)
			if current["repayment_plan_type"] == 1:
				Ulog.info(f"第{current['period']}期本金还款计划剩余应还金额校验通过")
			else:
				Ulog.info(f"第{current['period']}期利息还款计划剩余应还金额校验通过")

	@staticmethod
	def _business_type_2_repayment_plan(repay_data: dict) -> None:
		"""
		还款类型为2时的还款计划校验
		:param repay_data:
		:return:
		"""
		Ulog.info("业务类型为提前结清")
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
					Ulog.info("当前期新生成本金剩余应还金额/实际应还金额/原始应还金额/计划还款时间校验通过")
				else:
					assert_that(current["cur_amount"]).is_equal_to(repay_data["repay_interest"])
					assert_that(current["pay_amount"]).is_equal_to(repay_data["repay_interest"])
					assert_that(current["origin_amount"]).is_equal_to(interest)
					assert_that(current["pay_time"]).is_equal_to(repay_data["pay_time"])
					assert_that(current["rest_amount"]).is_equal_to(0)
					assert_that(current["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
					Ulog.info("当前期新生成利息剩余应还金额/实际应还金额/原始应还金额/计划还款时间校验通过")
			elif current["repayment_status"] == 9:
				status_9 += 1
				assert_that(current["cur_amount"]).is_equal_to(current["origin_amount"])
				assert_that(current["pay_amount"]).is_equal_to(0)
				Ulog.info("当前期已取消还款计划的当前应还金额/实还金额是否通过")
			assert_that(current["business_type"]).is_equal_to(2)
			Ulog.info("当前期的业务类型是否通过")
		assert_that(status_9).is_equal_to(2)
		assert_that(status_3).is_equal_to(2)
		Ulog.info("当前期还款计划条数校验通过")
		for before in repay_data["before_repayment_plan"]:
			assert_that(before["repayment_status"]).is_equal_to(3)
			assert_that(before["business_type"]).is_equal_to(1)
		assert_that(repay_data["before_repayment_plan"]).is_length(repay_data["period"] - 1)
		Ulog.info("已发生期还款计划条数/状态校验通过")
		for after in repay_data["after_repayment_plan"]:
			assert_that(after["repayment_status"]).is_equal_to(9)
			assert_that(after["business_type"]).is_equal_to(2)
		assert_that(repay_data["after_repayment_plan"]).is_length(
			(repay_data["maturity"] - repay_data["period"]) * 2)
		Ulog.info("未发生期还款计划条数/状态校验通过")

	@staticmethod
	def _business_type_3_repayment_plan(repay_data: dict) -> None:
		"""
		还款类型为3时的还款计划校验
		:param repay_data:
		:return:
		"""
		Ulog.info("业务类型为退货")
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
					Ulog.info("当前期本金剩余应还金额/实际应还金额/原始应还金额/计划还款时间校验通过")
				else:
					assert_that(current["cur_amount"]).is_equal_to(repay_data["repay_interest"])
					assert_that(current["pay_amount"]).is_equal_to(repay_data["repay_interest"])
					assert_that(current["origin_amount"]).is_equal_to(interest)
					assert_that(current["pay_time"]).is_equal_to(repay_data["pay_time"])
					assert_that(current["rest_amount"]).is_equal_to(0)
					assert_that(current["plan_pay_date"]).is_equal_to(repay_data["plan_pay_date"])
					Ulog.info("当前期本金剩余应还金额/实际应还金额/原始应还金额/计划还款时间校验通过")
			elif current["repayment_status"] == 9:
				status_9 += 1
				assert_that(current["cur_amount"]).is_equal_to(current["origin_amount"])
				assert_that(current["pay_amount"]).is_equal_to(0)
				if current["repayment_plan_type"] == 1:
					Ulog.info("当前期已取消本金还款计划的当前应还金额/实还金额校验通过")
				else:
					Ulog.info("当前期已取消利息还款计划的当前应还金额/实还金额校验通过")
			assert_that(current["business_type"]).is_equal_to(3)
			Ulog.info("当前期的业务类型校验通过")
		assert_that(status_9).is_equal_to(2)
		assert_that(status_3).is_equal_to(2)
		Ulog.info("当前期还款计划条数校验通过")
