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
	def check_column(info: str, environment: str, busi_id: str):
		map_dict = EntityInfo[info].value
		busi_type = info.split("_")[-1]
		sql_data = GetSqlData.select_extra_info(environment, busi_type, busi_id)
		for key, value in map_dict.items():
			Ulog.info(f"""校验参数:{key}是否落库""")
			assert_that(key in sql_data.keys()).is_true()

	@staticmethod
	def check_repayment_plan(is_repay: bool, env: str, project_id: str, param: Optional[dict]):
		if is_repay is True:
			repay_type = param["repayType"]
			period = param["period"]
			pay_time = param["payTime"]
			repayment_detail = param["repaymentDetailList"]
			maturity = GetSqlData.get_maturity(project_id=project_id, environment=env)
			database_repayment_plan = GetSqlData.get_repayment_plan(project_id=project_id, environment=env)
			current_repayment_plan = []
			before_repayment_plan = []
			after_repayment_plan = []
			re_amount = {
				1: 0,
				2: 0
			}
			for p in database_repayment_plan:
				if p["period"] == period:
					current_repayment_plan.append(p)
				elif p["period"] < period:
					before_repayment_plan.append(p)
				else:
					after_repayment_plan.append(p)
			for amount in repayment_detail:
				if amount["planCategory"] == 1:
					re_amount[1] = amount["payAmount"]
				elif amount["planCategory"] == 2:
					re_amount[2] = amount["payAmount"]
				else:
					pass
			if repay_type == 1:
				Ulog.info("业务类型为正常还款")
				assert_that(current_repayment_plan).is_length(2)
				Ulog.info("当前期还款计划条数校验成功")
				for current in current_repayment_plan:
					# 校验每一条还款计划的实际还款时间是否一致
					assert_that(current["pay_time"]).is_equal_to(pay_time)
					if current["repayment_plan_type"] == 1:
						Ulog.info(f"第{current['period']}期本金还款计划实还时间校验通过")
					else:
						Ulog.info(f"第{current['period']}期利息还款计划实还时间校验通过")
					# 校验每一条还款计划的实际还款金额是否一致
					assert_that(current["pay_amount"]).is_equal_to(re_amount[current["repayment_plan_type"]])
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
