# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2021-05-07 09:26:00
@describe: 通用用例
"""
import allure

from common.common_func import Common
from common.get_sql_data import GetSqlData
from typing import Optional
from datetime import date
from dateutil.relativedelta import relativedelta
from busi_assert.busi_asset import Assert


class Universal:

	@staticmethod
	@allure.step("修改数据至逾期")
	def overdue(
			period: int,
			environment: str,
			project_id: str,
			day: Optional[int] = None,
			month: Optional[int] = None,
			is_special_repurchase: Optional[bool] = False
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
		if is_special_repurchase is True:
			for i in range(6):
				GetSqlData.change_plan_pay_date(environment, project_id, period + i, plan_pay_date)
				GetSqlData.change_fee_plan_pay_date(environment, project_id, period + i, plan_pay_date)
		else:
			GetSqlData.change_plan_pay_date(environment, project_id, period, plan_pay_date)
			GetSqlData.change_fee_plan_pay_date(environment, project_id, period, plan_pay_date)
		Common().trigger_task("overdueForCloudloanJob", environment)
		Assert.check_overdue(period, environment, project_id)

	@staticmethod
	@allure.step("代偿")
	def compensation(
			period: int,
			environment: str,
			project_id: str,
			product: str
	) -> None:
		Universal.overdue(period, environment, project_id, 3)
		Universal._run_swap_task(product, environment)
		Assert.check_swap(period, environment, project_id)

	@staticmethod
	@allure.step("回购")
	def repurchase(
			period: int,
			environment: str,
			project_id: str,
			product: str
	) -> None:
		if product == "wxjk":
			Universal.overdue(period, environment, project_id, 3, is_special_repurchase=True)
			Universal._run_swap_task(product, environment)
		else:
			Universal.overdue(period, environment, project_id, 3)
			Universal._run_swap_task(product, environment)
			Universal.overdue(period, environment, project_id, 94)
			Universal.overdue(period + 1, environment, project_id, 3)
			Universal._run_swap_task(product, environment)
		Assert.check_swap(period, environment, project_id, False)

	@staticmethod
	def _run_swap_task(product: str, environment: str):
		products = {
			"jfx": ["assetSwapJob_XJ_JFX_YYDMUL", "assetSwapJob_XJ_JFX_YYDSIN"],
			"rmkj": "assetSwapJob_FQ_RM_RMYM",
			"jfq": ["assetSwapJob_FQ_JK_JFQJY", "assetSwapJob_FQ_JK_JFQJYV2", "assetSwapJob_FQ_JK_JFQYL",
					"assetSwapJob_FQ_JK_JFQYLV2"],
			"wxjk": ["assetSwapJob_XJ_WX_DDQ", "assetSwapJob_XJ_WX_KKD"],
			"ckshd": "assetSwapJob_FQ_JK_CKSHD",
			"cwshd": "assetSwapJob_FQ_JK_CWSHD"
		}
		if isinstance(products[product], list):
			for job in products[product]:
				Common.trigger_task(job, environment)
		else:
			Common.trigger_task(products[product], environment)