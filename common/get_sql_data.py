# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2019-08-09
@describe:获取数据库中信息
"""
import pymysql
import time
import sys
import os

from common.common_func import Common
from typing import Optional
from log.ulog import Ulog
from config.configer import Config

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class GetSqlData:

	@staticmethod
	def conn_database(environment, source: Optional[str] = "saas"):
		"""
		数据库连接
		:param source: str
		:type environment:str
		"""
		yaml_data = Common.get_yaml_data("config", "database.yaml")
		config = yaml_data[environment][source]
		config["cursorclass"] = pymysql.cursors.DictCursor
		try:
			connect = pymysql.connect(**config)
			return connect
		except Exception as e:
			raise e

	@staticmethod
	def exec_update(
			environment: str,
			sql: str,
			source: Optional[str] = "saas"
	):
		"""执行更新语句"""
		conn = None
		cur = None
		try:
			conn = GetSqlData.conn_database(environment, source)
			cur = conn.cursor()
			cur.execute(sql)
			conn.commit()
			Ulog.info(f"执行sql:{sql}")
		except Exception as e:
			conn.rollback()
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def exec_select(
			environment: str,
			sql: str,
			source: Optional[str] = "saas"
	) -> list:
		"""执行查询语句"""
		conn = None
		cur = None
		try:
			conn = GetSqlData.conn_database(environment, source)
			cur = conn.cursor()
			cur.execute(sql)
			Ulog.info(f"""执行查询语句:{sql}""")
			return cur.fetchall()
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_sub_table(environment: str, asset_id: int) -> str:
		# noinspection PyGlobalUndefined
		table = None
		if environment == "test":
			table = str((asset_id % 8 + 1))
		elif environment in ("qa", "prod"):
			table = str((asset_id >> 22) % 8 + 1)
		return table

	@staticmethod
	def check_credit_step(environment: str, credit_id: str) -> str:
		"""
		检查授信步骤
		"""
		# noinspection PyGlobalUndefined
		sql = f'''Select credit_step from sandbox_saas.credit where id = {credit_id};'''
		credit_step = GetSqlData.exec_select(environment, sql)[0].get("credit_step")
		return credit_step

	@staticmethod
	def change_credit_step(environment: str, credit_id: str) -> str:
		"""修改罗马车贷/车置宝授信信息"""
		# noinspection PyGlobalUndefined
		sql = """
			UPDATE sandbox_saas_centaur.apply 
			set approve_status='3',ds_success='3',indicator='{}' WHERE apply_id=%s;
			""" % credit_id
		GetSqlData.exec_update(environment, sql)

	@staticmethod
	def change_jfx_credit_step(environment: str, user_id: str) -> str:
		"""修改牙医贷授信信息"""
		# noinspection PyGlobalUndefined
		sql = f"""
			UPDATE sandbox_saas_athena.risk_apply 
			set audit_result='APPROVE',quota='300000.00',level='1',step='COMPLETED' 
			WHERE user_id={user_id};
			"""
		GetSqlData.exec_update(environment, sql)

	@staticmethod
	def change_credit_status(environment: str, credit_id: str) -> str:
		"""修改授信表状态与步骤"""
		# noinspection PyGlobalUndefined
		create_time = Common.get_new_time("before", "minutes", 10)
		sql = f"""update sandbox_saas.credit set create_time='{create_time}' where id='{credit_id}';"""
		GetSqlData.exec_update(environment, sql)

	@staticmethod
	def credit_set(environment: str, credit_id: str) -> str:
		"""授信时调用，根据环境判断是否需要等待补偿"""
		# noinspection PyGlobalUndefined
		Ulog.info("开始检查授信步骤")
		if Config().get_item("Switch", "credit") == "1":
			# GetSqlData.change_credit_step(environment, credit_id)
			GetSqlData.change_credit_status(environment, credit_id)
			GetSqlData.change_athena_status(environment, credit_id)
			Common.trigger_task(job_name="creditReparationJob", env=environment)
		status = 2
		version = 1
		while status != 4:
			if version > 20:
				Ulog.info("授信未成功")
				break
			step = GetSqlData().check_credit_step(environment, credit_id)
			if step != 4:
				Ulog.info(f"当前授信步骤为:{step:d};当前循环次数为:{version:d}")
				version += 1
				time.sleep(5)
			elif step == 4:
				Ulog.info("当前授信已完成,可以进行下个步骤!")
				status = 4

	@staticmethod
	def check_loan_result(environment: str, project_id: str) -> str:
		"""查询放款状态"""
		# noinspection PyGlobalUndefined
		sql = f"""Select loan_result from sandbox_saas.project_detail where id = {project_id};"""
		loan_result = GetSqlData.exec_select(environment, sql)[0].get('loan_result')
		return loan_result

	@staticmethod
	def loan_set(environment: str, project_id: str) -> str:
		"""放款申请后调用，查询放款状态是否成功"""
		# noinspection PyGlobalUndefined
		Ulog.info("开始检查放款步骤")

		# datas = '{"projectId":"%s","code":2000,"success":true,"inProcess":false}'%project_id
		# Ulog.info(datas)
		# rep = requests.post(url="http://api-qa1.cloudloan.com:9011/api/v1/busi/callback/loan/apply",
		# 			  data=datas)
		# Ulog.info(rep.status_code)
		# Ulog.info(rep.text)
		# http://api-qa1.cloudloan.com 39.107.43.201
		# while True:
		Common.trigger_task("projectLoanReparationJob", environment)
		if GetSqlData().check_loan_result(environment, project_id) == -1:
			raise Exception("放款状态不正确，未申请放款成功")
		else:
			try:
				version = 1
				while GetSqlData().check_loan_result(environment, project_id) != 1:
					if version > 100:
						Ulog.info(f"循环{version - 1}次未查询到放款成功状态，判断为放款失败")
						break
					res = GetSqlData().check_loan_result(environment, project_id)
					if res == 0:
						Ulog.info(f"当前loan_result为:{res};放款失败")
						break
					if res != 1:
						Ulog.info(f"当前loan_result为:{res};当前循环次数为:{version}")
						version += 1
						time.sleep(1)
			except Exception as e:
				raise e

	@staticmethod
	def check_pay_order_code(environment:str, project_id:str):
		"""检查steamrunner.pay_order的code"""
		# noinspection PyGlobalUndefined
		sql = f"""Select code from sandbox_saas_steamrunner.sr_pay_order where project_id = {project_id};"""
		code = GetSqlData.exec_select(environment, sql)[0].get("code")
		return code


	@staticmethod
	def change_pay_status(environment: str, project_id: str):
		"""修改steamrunner.pay_order的放款状态为成功"""
		# noinspection PyGlobalUndefined
		finish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		# finish_time = "2021-03-29 00:00:00"
		if Config().get_item("Switch", "loan") == '1':
			Ulog.info("放款开关已关闭，走虚拟放款逻辑")
			sql1 = f"""
				Update sandbox_saas_steamrunner.sr_pay_order 
				set code=2000,msg='成功',finish_time='{finish_time}' 
				where project_id={project_id};
				"""
			sql2 = f"""
				Update sandbox_saas.project_loan_flow
				set loan_result=2
				where project_id={project_id};
				"""
			sql3 = f"""
				Update sandbox_saas.project_loan_record
				set loan_result=2 
				where project_id={project_id};
				"""
			sql4 = f"""
				Update sandbox_saas.project_detail
				set loan_result=2,loan_status=0,loan_step=0
				where id={project_id};
				"""
			time.sleep(3)
			if GetSqlData.check_pay_order_code(environment, project_id) in (2002, 2003):
				sqls = [sql1, sql2, sql3, sql4]
			else:
				sqls = [sql1]
			for sql in sqls:
				GetSqlData.exec_update(environment, sql)
		else:
			Ulog.info("放款开关已开启,走真实放款流程")

	@staticmethod
	def get_asset_id(environment: str, project_id: str) -> str:
		"""获取资产id"""
		# noinspection PyGlobalUndefined
		sql = f"""select id from sandbox_saas.asset WHERE project_id={project_id};"""
		return GetSqlData.exec_select(environment, sql)[0].get("id")

	@staticmethod
	def get_user_repayment_detail(
			project_id: str,
			environment: str,
			period: int,
			repayment_plan_type: str,
			feecategory: int = 2002
	) -> dict:
		"""
		获取用户还款计划中的关联：
		渠道计划id
		计划还款时间
		剩余应还金额
		"""
		# noinspection PyGlobalUndefined, msg
		asset_id = GetSqlData.get_asset_id(environment, project_id)
		if repayment_plan_type in ["1", "2"]:
			plan_table = 'user_repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
			sql = f"""
				select * from {plan_table}
				where asset_id = {str(asset_id)}
				and period = {str(period)}
				and repayment_plan_type = {str(repayment_plan_type)};
				"""
		elif feecategory == 3003:
			plan_table = 'user_fee_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
			sql = f"""
				select * from {plan_table} 
				where asset_id = {str(asset_id)} 
				and period = {str(period)} and fee_category = {str(repayment_plan_type)};
				"""
		else:
			plan_table = 'fee_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
			sql = f"""
				select plan_pay_date,rest_amount,cur_amount,source_plan_id from {plan_table} 
				where asset_id = {str(asset_id)} and period = {str(period)} and fee_category = {feecategory};
				"""
		return GetSqlData.exec_select(environment, sql)[0]

	@staticmethod
	def get_user_repayment_amount(project_id: str, environment: str, period: str) -> str:
		"""获取用户还款计划当期应还款总额"""
		# noinspection PyGlobalUndefined
		asset_id = GetSqlData.get_asset_id(environment, project_id)
		plan_table = 'user_repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
		sql = f"""
			select sum(cur_amount) as cur_amount from {plan_table} 
			where asset_id={str(asset_id)} and period={str(period)};
			"""
		return float(GetSqlData.exec_select(environment, sql)[0].get('cur_amount'))

	@staticmethod
	def get_repayment_amount(project_id: str, environment: str, period: str) -> str:
		"""获取机构还款计划当期应还款总额"""
		# noinspection PyGlobalUndefined
		asset_id = GetSqlData.get_asset_id(environment, project_id)
		plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
		sql = f"""
			select sum(cur_amount) as amount from {plan_table} 
			where asset_id={str(asset_id)} and period={str(period)};
			"""
		return float(GetSqlData.exec_select(environment, sql)[0].get("amount"))

	@staticmethod
	def get_all_repayment_amount(project_id: str, environment: str) -> str:
		"""获取资产还款金额"""
		# noinspection PyGlobalUndefined
		sql = f"""select amount from sandbox_saas.asset where project_id='{project_id}';"""
		return float(GetSqlData.exec_select(environment, sql)[0].get('amount'))

	@staticmethod
	def get_maturity(project_id: str, environment: str) -> str:
		"""获取资产期数"""
		# noinspection PyGlobalUndefined
		sql = f'''select maturity from sandbox_saas.asset where project_id="{project_id}";'''
		return GetSqlData.exec_select(environment, sql)[0].get("maturity")

	@staticmethod
	def get_repayment_principal(project_id: str, environment: str, period: str) -> str:
		"""获取机构还款计划应还本金"""
		# noinspection PyGlobalUndefined
		asset_id = GetSqlData.get_asset_id(environment, project_id)
		plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
		sql = f"""
			select origin_amount 
			from {plan_table} 
			where asset_id={str(asset_id)} 
			and period={str(period)} 
			and repayment_plan_type=1;
			"""
		return str(GetSqlData.exec_select(environment, sql)[0].get("origin_amount"))

	@staticmethod
	def get_debt_amount(project_id, environment):
		"""获取资产剩余应还本金"""
		# noinspection PyGlobalUndefined
		asset_id = GetSqlData.get_asset_id(environment, project_id)
		sql = f"""select debt_amount from sandbox_saas.asset where id={asset_id}"""
		return GetSqlData.exec_select(environment, sql)[0].get('debt_amount')

	@staticmethod
	def get_repayment_detail(
			project_id: str,
			environment: str,
			period: str,
			repayment_plan_type: str
	) -> dict:
		"""
		获取机构还款计划中的关联：
		渠道计划id
		计划还款时间
		剩余应还金额
		"""
		# noinspection PyGlobalUndefined
		asset_id = GetSqlData.get_asset_id(environment, project_id)
		plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
		sql = f"""
			select * 
			from {plan_table} 
			where asset_id = {asset_id} 
			and period = {period} 
			and repayment_plan_type = {repayment_plan_type};
			"""
		return GetSqlData.exec_select(environment, sql)[0]

	@staticmethod
	def check_user_amount(user_id, environment):
		"""持续查询用户可用额度"""
		version = 1
		while True:
			if version > 10:
				Ulog.info(f'''当前查询次数{version}''')
				break
			user_amount = GetSqlData.user_amount(user_id, environment)
			if user_amount > 0.00:
				Ulog.info("额度检查完成")
				break
			elif user_amount == 0.000000:
				version += 1
				time.sleep(5)

	@staticmethod
	def user_amount(user_id: str, environment: str):
		"""查询用户可用额度"""
		# noinspection PyGlobalUndefined, availableAmount
		sql = f'select available_amount from sandbox_saas_nebula.amount where user_id={user_id};'
		return GetSqlData.exec_select(environment, sql)[0].get('available_amount')

	@staticmethod
	def project_audit_status(project_id: str, environment: str) -> int:
		"""查询进件审核状态"""
		# noinspection PyGlobalUndefined, audit_status
		sql = f"""select audit_status from sandbox_saas.project_detail where id={project_id};"""
		audit_status = GetSqlData.exec_select(environment, sql)[0].get('audit_status')
		return audit_status

	@staticmethod
	def project_result(project_id: str, environment: str) -> str:
		"""进件审核结果查询"""
		Ulog.info("开始检查进件审核步骤")
		try:
			version = 1
			while True:
				if version > 10:
					Ulog.info(f"{version}次未查询到进件审核成功状态")
					break
				audit_status = GetSqlData().project_audit_status(project_id, environment)
				if audit_status != 2:
					Ulog.info(f"当前进件审核状态为:{audit_status};当前查询次数为:{version}")
					version += 1
					time.sleep(10)
				elif audit_status == 2:
					Ulog.info("进件审核成功")
					break
		except Exception as e:
			raise e

	@staticmethod
	def change_project_audit_status(project_id: str, environment: str):
		"""修改进件审核状态为通过"""
		# noinspection PyGlobalUndefined
		if Config().get_item("Switch", "project") == '1':
			Ulog.info("风控已关闭，走虚拟进件风控逻辑")
			sql = f"""
						UPDATE sandbox_saas.project_detail
						SET audit_status = 2, audit_result = 1, project_step = 5
						WHERE id = {project_id};
					"""
			GetSqlData.exec_update(environment, sql)
		else:
			Ulog.info("风控开关已开启，走真实风控流程")
			GetSqlData.project_result(project_id, environment)

	@staticmethod
	def check_project_audit_status(project_id: str, environment: str) -> int:
		"""查询进件审核状态"""
		# noinspection PyGlobalUndefined
		sql = f"""select audit_status from sandbox_saas.project_detail where id={project_id};"""
		return GetSqlData.exec_select(environment, sql)[0].get('audit_status')

	@staticmethod
	def loan_sql(env: str):
		"""修改steamrunner放款状态"""
		# noinspection PyGlobalUndefined
		sql1 = f"""UPDATE sandbox_saas.project_loan_record
					SET loan_result = 2
					WHERE project_id IN (
							SELECT id
							FROM sandbox_saas.project_detail
							WHERE product_code IN (
									'XJ_JFX_YYDSIN', 
									'XJ_JFX_YYDMUL', 
									'FQ_RM_RMYM', 
									'XJ_ROMA_CAR', 
									'XJ_ROMA_CARV2', 
									'XJ_DX_SYJV2', 
									'XJ_DX_SYJ', 
									'FQ_JK_JFQYL', 
									'FQ_JK_JFQYLV2', 
									'FQ_JK_JFQJY', 
									'FQ_JK_JFQJYV2',
									'XJ_WX_DDQ',
									'XJ_WX_KKD'
								)
								AND project_detail.loan_result != 1
					)
					AND loan_result = 0;"""
		sql2 = f"""UPDATE sandbox_saas_steamrunner.sr_pay_order
					SET code = 2000
					WHERE project_id IN (
							SELECT id
							FROM sandbox_saas.project_detail
							WHERE product_code IN (
								'XJ_JFX_YYDSIN', 
								'XJ_JFX_YYDMUL', 
								'FQ_RM_RMYM', 
								'XJ_ROMA_CAR', 
								'XJ_ROMA_CARV2', 
								'XJ_DX_SYJV2', 
								'XJ_DX_SYJ', 
								'FQ_JK_JFQYL', 
								'FQ_JK_JFQYLV2', 
								'FQ_JK_JFQJY', 
								'FQ_JK_JFQJYV2',
								'XJ_WX_DDQ',
								'XJ_WX_KKD'
							)
							AND project_detail.loan_result != 1
						);"""
		sql3 = f"""UPDATE sandbox_saas.project_detail
				SET loan_result = 2
				WHERE id IN (
						SELECT a.project_id
						FROM (
							SELECT project_id
							FROM sandbox_saas.project_loan_flow
							WHERE project_id IN (
								SELECT id
								FROM sandbox_saas.project_detail
								WHERE (product_code IN (
										'XJ_JFX_YYDSIN', 
										'XJ_JFX_YYDMUL', 
										'FQ_RM_RMYM', 
										'XJ_ROMA_CAR', 
										'XJ_ROMA_CARV2', 
										'XJ_DX_SYJV2', 
										'XJ_DX_SYJ', 
										'FQ_JK_JFQYL', 
										'FQ_JK_JFQYLV2', 
										'FQ_JK_JFQJY', 
										'FQ_JK_JFQJYV2', 
										'XJ_WX_DDQ', 
										'XJ_WX_KKD'
									)
									AND loan_result != 1
									AND audit_result = 1)
							)
						) a
					);"""
		sql4 = f"""UPDATE sandbox_saas.project_loan_flow
					SET loan_result = 2
					WHERE product_code IN (
							'XJ_JFX_YYDSIN', 
							'XJ_JFX_YYDMUL', 
							'FQ_RM_RMYM', 
							'XJ_ROMA_CAR', 
							'XJ_ROMA_CARV2', 
							'XJ_DX_SYJV2', 
							'XJ_DX_SYJ', 
							'FQ_JK_JFQYL', 
							'FQ_JK_JFQYLV2', 
							'FQ_JK_JFQJY', 
							'FQ_JK_JFQJYV2',
							'XJ_WX_DDQ',
							'XJ_WX_KKD'
						)
						AND loan_result != 1;"""
		sql_list = [sql1, sql2, sql3, sql4]
		for sql in sql_list:
			GetSqlData.exec_update(environment=env, sql=sql)

	@staticmethod
	def select_asset() -> int:
		"""查询没有放款成功的进件数量"""
		# noinspection PyGlobalUndefined
		sql = f"""SELECT COUNT(DISTINCT project_id) AS c
					FROM sandbox_saas.project_loan_flow
					WHERE project_id IN (
						SELECT id
						FROM sandbox_saas.project_detail
						WHERE product_code IN (
								'XJ_JFX_YYDSIN', 
								'XJ_JFX_YYDMUL', 
								'FQ_RM_RMYM', 
								'XJ_ROMA_CAR', 
								'XJ_ROMA_CARV2', 
								'XJ_DX_SYJV2', 
								'XJ_DX_SYJ', 
								'FQ_JK_JFQYL', 
								'FQ_JK_JFQYLV2', 
								'FQ_JK_JFQJY', 
								'FQ_JK_JFQJYV2', 
								'XJ_WX_DDQ', 
								'XJ_WX_KKD', 
								'XJ_WX_DDQ', 
								'XJ_WX_KKD'
							)
							AND loan_result != 1
					);
				"""
		return GetSqlData.exec_select("qa", sql)[0].get("c")

	@staticmethod
	def get_current_period(project_id: str, environment: str) -> int:
		"""获取资产当前发生期"""
		# noinspection PyGlobalUndefined
		asset_id = GetSqlData.get_asset_id(environment, project_id)
		plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
		sql = f"""select period 
				from sandbox_saas.{plan_table} 
				where asset_id={asset_id} 
				and repayment_status=1 
				order by period limit 1
				"""
		period = GetSqlData.exec_select(environment, sql)[0].get('period')
		return period

	@staticmethod
	def get_prod_project_id(asset_id: str):
		"""获取进件ID"""
		# noinspection PyGlobalUndefined
		sql = f"""select project_id from saas_zhtb where asset_id={asset_id}"""
		return GetSqlData.exec_select("prod", sql)[0].get("project_id")

	@staticmethod
	def get_contact_id(project_id: str):
		"""获取合同ID"""
		# noinspection PyGlobalUndefined
		sql = f"""select id from saas_zhtb where association_id={project_id}"""
		return GetSqlData.exec_select("prod", sql)[0].get("id")

	@staticmethod
	def like_asset_id(asset_id: str, environment: str):
		"""资产ID模糊查询"""
		# noinspection PyGlobalUndefined
		sql = f"""select id from asset where id like '{asset_id}';"""
		return GetSqlData.exec_select(environment, sql)[0].get('id')

	@staticmethod
	def asset_count(environment: str):
		"""查询资产ID"""
		# noinspection PyGlobalUndefined
		sql = "select id from asset;"
		asset_id = GetSqlData.exec_select(environment, sql)
		ids = []
		for i in asset_id:
			ids.append(i.get('id'))
		return ids

	@staticmethod
	def repayment_plan(asset_id: str, environment: str) -> int:
		"""查询机构还款计划条数"""
		# noinspection PyGlobalUndefined, plan_table
		plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
		sql = f"""select count(*) as c from {plan_table} where asset_id={asset_id};"""
		count = GetSqlData.exec_select(environment, sql)[0].get('c')
		return count

	@staticmethod
	def select_need_audit_project_ids() -> list:
		"""
		查询要修改审核状态的进件ID
		用于Job
		"""
		# noinspection PyGlobalUndefined
		sql = f"""SELECT id
				FROM project_detail
				WHERE product_code IN (
						'XJ_JFX_YYDSIN', 
						'XJ_JFX_YYDMUL', 
						'FQ_RM_RMYM', 
						'XJ_ROMA_CAR', 
						'XJ_ROMA_CARV2', 
						'XJ_DX_SYJV2', 
						'XJ_DX_SYJ', 
						'FQ_JK_JFQYL', 
						'FQ_JK_JFQYLV2', 
						'FQ_JK_JFQJY', 
						'FQ_JK_JFQJYV2', 
						'XJ_WX_DDQ', 
						'XJ_WX_KKD', 
						'XJ_WX_DDQ', 
						'XJ_WX_KKD'
					)
					AND audit_status != 2"""
		ids = GetSqlData.exec_select("qa", sql)
		idss = []
		for i in ids:
			idss.append(i.get("id"))
		return idss

	@staticmethod
	def change_audit():
		"""
		修改进件审核状态
		用于Job
		"""
		# noinspection PyGlobalUndefined
		sql1 = f"""
				update project_detail 
				set audit_status=2,audit_result=1
				where product_code in ("FQ_JK_JFQYL", "FQ_JK_JFQJY");
				"""
		GetSqlData.exec_update(environment="qa", sql=sql1)

	@staticmethod
	def change_athena_status(environment: str, apply_id: str):
		"""修改Athena数据状态"""
		# noinspection PyGlobalUndefined
		sql = f"""
				update sandbox_saas_athena.risk_apply 
				set audit_result='APPROVE',quota=300000,step='COMPLETED',return_code=2000 
				where apply_id='{apply_id}';
				"""
		GetSqlData.exec_update(environment, sql)

	@staticmethod
	def change_plan_pay_date(environment: str, project_id: str, period: int):
		"""修改还款计划应还时间"""
		# noinspection PyGlobalUndefined
		asset_id = GetSqlData.get_asset_id(environment, project_id)
		table = "repayment_plan_0" + GetSqlData.get_sub_table(environment, asset_id)
		sql = f"""
				update sandbox_saas.{table}
				set plan_pay_date='{Common.get_time("day")}'
				where asset_id='{asset_id}' and period={period};
				"""
		GetSqlData.exec_update(environment, sql)
