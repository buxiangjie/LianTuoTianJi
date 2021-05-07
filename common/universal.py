# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2021-05-07 09:26:00
@describe: 通用用例
"""
from common.common_func import Common
from common.get_sql_data import GetSqlData
from typing import Optional
from datetime import date
from dateutil.relativedelta import relativedelta
from busi_assert.busi_asset import Assert


class Universal:

	@staticmethod
	def overdue(
			period: int,
			environment: str,
			project_id: str,
			day: Optional[int] = None,
			month: Optional[int] = None
	):
		plan_pay_date = None
		if all([day, month]):
			raise IOError("逾期时间只能有一个")
		elif (day is None) & (month is None):
			raise IOError("逾期时间至少有一个")
		elif day is not None:
			plan_pay_date = Common.get_new_time("before", "days", day).split(" ")[0]
		elif month is not None:
			plan_pay_date = str(date.today() - relativedelta(months=month)).split(" ")[0]
		GetSqlData.change_plan_pay_date(environment, project_id, period, plan_pay_date)
		GetSqlData.change_fee_plan_pay_date(environment, project_id, period, plan_pay_date)
		Common().trigger_task("overdueForCloudloanJob", environment)
		Assert.check_overdue(period, environment, project_id)
