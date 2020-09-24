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
from common.get_sql_data import GetSqlData
from selenium import webdriver
from selenium.webdriver.common.by import By
from common.common_func import Common


class Ob(object):
	globals()['driver'] = ' '

	@staticmethod
	def dr():
		global driver
		if sys.platform == 'darwin':
			driver = webdriver.Firefox(
				executable_path=f'{os.path.dirname(os.path.abspath(__file__))}/drivers/geckodriver_mac')
		elif sys.platform == 'win32':
			driver = webdriver.Firefox(
				executable_path=f'{os.path.dirname(os.path.abspath(__file__))}/drivers/geckodriver_windows.exe')
		globals()['driver'] = driver
		driver.get("http://47.95.115.237:8899/#")
		time.sleep(8)

	@staticmethod
	def loan_job():
		try:
			print(f"当前未放款成功的产品数量为:{GetSqlData.select_asset()}")
			GetSqlData.loan_sql('qa')
			# Ob().trigger()
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

	@staticmethod
	def trigger():
		# (username="root_zhtb", password="LQd6rUYW8f")
		try:
			globals()['driver'].refresh()
			time.sleep(4)
			globals()['driver'].set_window_size(1440, 900)
			time.sleep(3)
			globals()['driver'].find_element(By.CSS_SELECTOR, ".fa-tasks").click()
			time.sleep(4)
			globals()['driver'].find_element(By.CSS_SELECTOR, "#job-status > .fa").click()
			time.sleep(4)
			globals()['driver'].find_element(By.CSS_SELECTOR, ".form-control").click()
			time.sleep(4)
			globals()['driver'].find_element(By.CSS_SELECTOR, ".form-control").send_keys("projectLoanReparationJob")
			time.sleep(4)
			globals()['driver'].find_element(By.CSS_SELECTOR, ".btn-xs:nth-child(3)").click()
		except Exception as e:
			print(e)


if __name__ == '__main__':
	# Ob.dr()
	# schedule.every(1).minutes.do(Ob.loan_job)
	# schedule.every(5).seconds.do(Ob.project_job)
	# schedule.every(1).minutes.do(runn)
	# while True:
	# 	schedule.run_pending()

	scheduler = BlockingScheduler()
	scheduler.add_job(Ob.loan_job, 'interval', seconds=15)
	scheduler.start()
