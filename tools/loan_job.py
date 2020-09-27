# -*- coding: UTF-8 -*-
"""
@auth:
@date:
@describe:
"""
import time
import random
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from common.get_sql_data import GetSqlData
from common.common_func import Common


class Ob(object):

	@staticmethod
	def loan_job():
		try:
			print(f"当前未放款成功的产品数量为:{GetSqlData.select_asset()}")
			GetSqlData.loan_sql('qa')
			Common.trigger_task("projectLoanReparationJob", "qa")
			print(f"执行完成,任务编号为{str(random.random()).split('.')[1]}")
		except Exception as e:
			print(e)

	@staticmethod
	def project_job():
		try:
			print("开始查询审核未通过的即分期进件")
			ids = GetSqlData.select_need_audit_project_ids()
			print(f"应当修改的进件ID:{ids}")
			print("开始执行修改sql")
			GetSqlData.change_audit()
			print("执行完成")
		except Exception as e:
			raise e


scheduler = BlockingScheduler()
scheduler.add_job(Ob.loan_job, 'interval', seconds=15)
scheduler.add_job(Ob.project_job, 'interval', seconds=15)
scheduler.start()
