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
		"""
		:param period: 1
		:param environment: test/qa
		:param project_id: str
		:param day: int
		:param month: int
		:param is_special_repurchase: 如果产品为卡卡贷/豆豆钱,则该字段值为True
		:return:
		"""
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
		"""
		:param period: 1
		:param environment: test/qa
		:param project_id: str
		:param product: str, 'jfx,rmkj,jfq,ckshd,cwshd,wxjk'
		:return: None
		"""
		if product == "wxjk":
			Universal.overdue(period, environment, project_id, 1)
		else:
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
		"""
		:param period: 1
		:param environment: test/qa
		:param project_id: str
		:param product: str, 'jfx,rmkj,jfq,ckshd,cwshd,wxjk'
		:return: None
		"""
		if product == "wxjk":
			Universal.overdue(period, environment, project_id, 1, is_special_repurchase=True)
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
		"""
		运行债转任务
		:param product:
		:param environment:
		:return:
		"""
		products = {
			"jfx": ["XJ_JFX_YYDMUL", "XJ_JFX_YYDSIN"],
			"rmkj": "FQ_RM_RMYM",
			"jfq": ["FQ_JK_JFQJY", "FQ_JK_JFQJYV2", "FQ_JK_JFQYL", "FQ_JK_JFQYLV2"],
			"wxjk": ["XJ_WX_DDQ", "XJ_WX_KKD"],
			"ckshd": "FQ_JK_CKSHD",
			"cwshd": "FQ_JK_CWSHD"
		}
		if isinstance(products[product], list):
			for job in products[product]:
				Common.trigger_task("assetSwapJob/" + job, environment)
		else:
			Common.trigger_task("assetSwapJob/" + products[product], environment)
