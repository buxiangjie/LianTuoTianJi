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
from log.ulog import Ulog
from config.configer import Config
from log.logger import Logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger = Ulog().getlog()


class GetSqlData(object):

	@staticmethod
	def conn_database(environment, source='saas'):
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
	def get_sub_table(environment, asset_id):
		# noinspection PyGlobalUndefined
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
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f'''Select credit_step from sandbox_saas.credit where id = {credit_id};'''
			cur.execute(sql)
			credit_step = cur.fetchone().get('credit_step')
			return int(credit_step)
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def change_credit_step(environment: str, credit_id: str) -> str:
		"""修改罗马车贷/车置宝授信信息"""
		# noinspection PyGlobalUndefined
		conn = GetSqlData.conn_database(environment)
		try:
			cur = conn.cursor()
			sql = """
				UPDATE sandbox_saas_centaur.apply 
				set approve_status='3',ds_success='3',indicator='{}' WHERE apply_id=%s;
				""" % credit_id
			cur.execute(sql)
			conn.commit()
		except Exception as e:
			conn.rollback()
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def change_jfx_credit_step(environment: str, user_id: str) -> str:
		"""修改牙医贷授信信息"""
		# noinspection PyGlobalUndefined
		conn = GetSqlData.conn_database(environment)
		try:
			cur = conn.cursor()
			sql = f"""
				UPDATE sandbox_saas_athena.risk_apply 
				set audit_result='APPROVE',quota='300000.00',level='1',step='COMPLETED' 
				WHERE user_id={user_id};
				"""
			cur.execute(sql)
			conn.commit()
		except Exception as e:
			conn.rollback()
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def change_credit_status(environment: str, credit_id: str) -> str:
		"""修改授信表状态与步骤"""
		# noinspection PyGlobalUndefined
		conn = GetSqlData.conn_database(environment)
		try:
			cur = conn.cursor()
			create_time = Common.get_new_time("before", "minutes", 10)
			sql = f"""update sandbox_saas.credit set create_time='{create_time}' where id='{credit_id}';"""
			cur.execute(sql)
			conn.commit()
		except Exception as e:
			conn.rollback()
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def credit_set(environment: str, credit_id: str) -> str:
		"""授信时调用，根据环境判断是否需要等待补偿"""
		# noinspection PyGlobalUndefined
		logger.info("开始检查授信步骤")
		if Config().get_item("Switch", "credit") == "1":
			# GetSqlData.change_credit_step(environment, credit_id)
			GetSqlData.change_credit_status(environment, credit_id)
			GetSqlData.change_athena_status(environment, credit_id)
		status = 2
		version = 1
		while status != 4:
			if version > 10:
				logger.info("授信未成功")
				break
			step = GetSqlData().check_credit_step(environment, credit_id)
			if step != 4:
				logger.info(f"当前授信步骤为:{step:d};当前循环次数为:{version:d}")
				version += 1
				time.sleep(10)
			elif step == 4:
				logger.info("当前授信已完成,可以进行下个步骤!")
				status = 4

	@staticmethod
	def check_loan_result(environment: str, project_id: str) -> str:
		"""查询放款状态"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f'''Select loan_result from sandbox_saas.project_detail where id = {project_id};'''
			cur.execute(sql)
			loan_result = cur.fetchone().get('loan_result')
			print(f"loan_result:{loan_result}")
			return loan_result
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def loan_set(environment: str, project_id: str) -> str:
		"""放款申请后调用，查询放款状态是否成功"""
		# noinspection PyGlobalUndefined
		logger.info("开始检查放款步骤")
		Common.trigger_task("projectLoanReparationJob", environment)
		time.sleep(15)
		if GetSqlData().check_loan_result(environment, project_id) == -1:
			raise Exception("放款状态不正确，未申请放款成功")
		else:
			try:
				version = 1
				while GetSqlData().check_loan_result(environment, project_id) != 1:
					if version > 100:
						logger.info(f"循环{version - 1}次未查询到放款成功状态，判断为放款失败")
						break
					res = GetSqlData().check_loan_result(environment, project_id)
					if res == 0:
						logger.info(f"当前loan_result为:{res};放款失败")
						break
					if res != 1:
						logger.info(f"当前loan_result为:{res};当前循环次数为:{version}")
						version += 1
						time.sleep(5)
			except Exception as e:
				raise e

	@staticmethod
	def change_pay_status(environment: str, project_id: str):
		"""修改steamrunner.pay_order的放款状态为成功"""
		# noinspection PyGlobalUndefined
		finish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		if Config().get_item("Switch", "loan") == '1':
			logger.info("放款开关已关闭，走虚拟放款逻辑")
			time.sleep(5)
			try:
				conn = GetSqlData.conn_database(environment, source='steamrunner')
				cur = conn.cursor()
				sql = f"""
					Update sandbox_saas_steamrunner.sr_pay_order 
					set code=2000,msg='成功',finish_time='{finish_time}' 
					where project_id={project_id}
					"""
				cur.execute(sql)
				conn.commit()
			except Exception as e:
				conn.rollback()
				raise e
			finally:
				cur.close()
				conn.close()
		else:
			logger.info("放款开关已开启,走真实放款流程")

	@staticmethod
	def get_asset_id(environment: str, project_id: str) -> str:
		"""获取资产id"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""select id from sandbox_saas.asset WHERE project_id={project_id};"""
			cur.execute(sql)
			msg = cur.fetchone().get("id")
			return msg
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_user_repayment_detail(project_id, environment, period, repayment_plan_type, feecategory=2002) -> dict:
		"""
		获取用户还款计划中的关联：
		渠道计划id
		计划还款时间
		剩余应还金额
		:rtype:
		"""
		# noinspection PyGlobalUndefined, msg
		try:
			asset_id = GetSqlData.get_asset_id(environment, project_id)
			if repayment_plan_type in ["1", "2"]:
				plan_table = 'user_repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
				sql = f"""
					select * from {plan_table}
					where asset_id = {str(asset_id)}
					and period = {str(period)}
					and repayment_plan_type = {str(repayment_plan_type)};
					"""
				conn = GetSqlData.conn_database(environment)
				cur = conn.cursor()
			elif feecategory == 3003:
				plan_table = 'user_fee_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
				sql = f"""
					select * from {plan_table} 
					where asset_id = {str(asset_id)} 
					and period = {str(period)} and fee_category = {str(repayment_plan_type)};
					"""
				conn = GetSqlData.conn_database(environment)
				cur = conn.cursor()
			else:
				plan_table = 'fee_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
				sql = f"""
					select plan_pay_date,rest_amount,cur_amount,source_plan_id from {plan_table} 
					where asset_id = {str(asset_id)} and period = {str(period)} and fee_category = {feecategory};
					"""
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			cur.execute(sql)
			msg = cur.fetchone()
			return msg
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_user_repayment_amount(project_id: str, environment: str, period: str) -> str:
		"""获取用户还款计划当期应还款总额"""
		# noinspection PyGlobalUndefined
		try:
			asset_id = GetSqlData.get_asset_id(environment, project_id)
			plan_table = 'user_repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""
				select sum(cur_amount) as cur_amount from {plan_table} 
				where asset_id={str(asset_id)} and period={str(period)};
				"""
			cur.execute(sql)
			amount = cur.fetchone().get('cur_amount')
			return float(amount)
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_repayment_amount(project_id: str, environment: str, period: str) -> str:
		"""获取机构还款计划当期应还款总额"""
		# noinspection PyGlobalUndefined
		try:
			asset_id = GetSqlData.get_asset_id(environment, project_id)
			plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""
				select sum(cur_amount) as amount from {plan_table} 
				where asset_id={str(asset_id)} and period={str(period)};
				"""
			cur.execute(sql)
			amount = cur.fetchone().get("amount")
			return float(amount)
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_all_repayment_amount(project_id: str, environment: str) -> str:
		"""获取资产还款金额"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""select amount from sandbox_saas.asset where project_id='{project_id}';"""
			cur.execute(sql)
			amount = cur.fetchone().get('amount')
			return float(amount)
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_maturity(project_id: str, environment: str) -> str:
		"""获取资产期数"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f'''select maturity from sandbox_saas.asset where project_id="{project_id}";'''
			cur.execute(sql)
			maturity = cur.fetchone().get("maturity")
			return maturity
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_repayment_principal(project_id: str, environment: str, period: str) -> str:
		"""获取机构还款计划应还本金"""
		# noinspection PyGlobalUndefined
		try:
			asset_id = GetSqlData.get_asset_id(environment, project_id)
			plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""
				select origin_amount 
				from {plan_table} 
				where asset_id={str(asset_id)} 
				and period={str(period)} 
				and repayment_plan_type=1;
				"""
			cur.execute(sql)
			amount = cur.fetchone()[0]
			return str(amount)
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_debt_amount(project_id, environment):
		"""获取资产剩余应还本金"""
		# noinspection PyGlobalUndefined
		try:
			asset_id = GetSqlData.get_asset_id(environment, project_id)
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""select debt_amount from sandbox_saas.asset where id={asset_id}"""
			cur.execute(sql)
			debt = cur.fetchone().get('debt_amount')
			return debt
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_repayment_detail(project_id: str, environment: str, period: str, repayment_plan_type: str) -> dict:
		"""
		获取机构还款计划中的关联：
		渠道计划id
		计划还款时间
		剩余应还金额
		:rtype: object
		"""
		# noinspection PyGlobalUndefined
		try:
			asset_id = GetSqlData.get_asset_id(environment, project_id)
			plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""
				select * 
				from {plan_table} 
				where asset_id = {asset_id} 
				and period = {period} 
				and repayment_plan_type = {repayment_plan_type};
				"""
			cur.execute(sql)
			msg = cur.fetchone()
			return msg
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def check_user_amount(user_id, environment):
		"""持续查询用户可用额度"""
		version = 1
		while True:
			if version > 10:
				logger.info(f'''当前查询次数{version}''')
				break
			user_amount = GetSqlData.user_amount(user_id, environment)
			if user_amount > 0.00:
				logger.info("额度检查完成")
				break
			elif user_amount == 0.000000:
				version += 1
				time.sleep(5)

	@staticmethod
	def user_amount(user_id, environment):
		"""查询用户可用额度"""
		# noinspection PyGlobalUndefined, availableAmount
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f'select available_amount from sandbox_saas_nebula.amount where user_id={user_id};'
			cur.execute(sql)
			available_amount = cur.fetchone().get('available_amount')
			return available_amount
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def project_audit_status(project_id: str, environment: str) -> int:
		"""查询进件审核状态"""
		# noinspection PyGlobalUndefined, audit_status
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f'select audit_status from sandbox_saas.project_detail where id={project_id};'
			cur.execute(sql)
			audit_status = cur.fetchone().get('audit_status')
			return audit_status
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def project_result(project_id: str, environment: str) -> str:
		"""进件审核结果查询"""
		logger.info("开始检查进件审核步骤")
		try:
			version = 1
			while True:
				if version > 10:
					logger.info(f"{version}次未查询到进件审核成功状态")
					break
				audit_status = GetSqlData().project_audit_status(project_id, environment)
				if audit_status != 2:
					logger.info(f"当前进件审核状态为:{audit_status};当前查询次数为:{version}")
					version += 1
					time.sleep(10)
				elif audit_status == 2:
					logger.info("进件审核成功")
					break
		except Exception as e:
			raise e

	@staticmethod
	def change_project_audit_status(project_id: str, environment: str) -> str:
		"""修改进件审核状态为通过"""
		# noinspection PyGlobalUndefined
		if Config().get_item("Switch", "project") == '1':
			logger.info("风控已关闭，走虚拟进件风控逻辑")
			try:
				conn = GetSqlData.conn_database(environment)
				cur = conn.cursor()
				sql = f'update sandbox_saas.project_detail set audit_status=2,audit_result=1,project_step=5 where id={project_id};'
				cur.execute(sql)
				conn.commit()
			except Exception as e:
				raise e
			finally:
				cur.close()
				conn.close()
		else:
			logger.info("风控开关已开启，走真实风控流程")
			GetSqlData.project_result(project_id, environment)

	@staticmethod
	def check_project_audit_status(project_id: str, environment: str) -> int:
		"""查询进件审核状态"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f'select audit_status from sandbox_saas.project_detail where id={project_id};'
			cur.execute(sql)
			conn.commit()
			audit_status = cur.fetchone().get('audit_status')
			return audit_status
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def loan_sql(env):
		"""修改steamrunner放款状态"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database(env)
			cur = conn.cursor()
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
			cur.execute(sql1)
			cur.execute(sql2)
			cur.execute(sql3)
			cur.execute(sql4)
			conn.commit()
		except Exception as e:
			conn.rollback()
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def select_asset():
		"""查询没有放款成功的进件数量"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database("qa")
			cur = conn.cursor()
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
			cur.execute(sql)
			conn.commit()
			coun = cur.fetchone().get("c")
			return coun
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_current_period(project_id, environment):
		"""获取资产当前发生期"""
		# noinspection PyGlobalUndefined
		try:
			asset_id = GetSqlData.get_asset_id(environment, project_id)
			plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""select period 
					from sandbox_saas.{plan_table} 
					where asset_id={asset_id} 
					and repayment_status=1 
					order by period limit 1
					"""
			cur.execute(sql)
			period = cur.fetchone().get('period')
			return period
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_prod_project_id(asset_id):
		"""获取进件ID"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database('prod')
			cur = conn.cursor()
			sql = f"""select project_id from saas_zhtb where asset_id={asset_id}"""
			cur.execute(sql)
			project_id = cur.fetchone()[0]
			return project_id
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_contact_id(project_id):
		"""获取合同ID"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database('prod')
			cur = conn.cursor()
			sql = f"""select id from saas_zhtb where association_id={project_id}"""
			cur.execute(sql)
			contact_id = cur.fetchone()[0]
			return contact_id
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def like_asset_id(asset_id, environment):
		"""资产ID模糊查询"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""select id from asset where id like '{asset_id}';"""
			cur.execute(sql)
			asset_id = cur.fetchone().get('id')
			return asset_id
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def asset_count(environment):
		"""查询资产ID"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = "select id from asset;"
			cur.execute(sql)
			asset_id = cur.fetchall()
			ids = []
			for i in asset_id:
				ids.append(i.get('id'))
			return ids
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def repayment_plan(asset_id: str, environment: str) -> int:
		"""查询机构还款计划条数"""
		# noinspection PyGlobalUndefined, plan_table
		try:
			conn = GetSqlData.conn_database(environment)
			plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asset_id)
			cur = conn.cursor()
			sql = f"""select count(*) as c from {plan_table} where asset_id={asset_id};"""
			cur.execute(sql)
			count = cur.fetchone().get('c')
			return int(count)
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def select_need_audit_project_ids() -> list:
		"""
		查询要修改审核状态的进件ID
		用于Job
		"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database("qa")
			cur = conn.cursor()
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
			cur.execute(sql)
			ids = cur.fetchall()
			idss = []
			for i in ids:
				idss.append(i.get("id"))
			return idss
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def change_audit():
		"""
		修改进件审核状态
		用于Job
		"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database("qa")
			cur = conn.cursor()
			sql1 = f"""update project_detail set audit_status=2,audit_result=1 where product_code in ("FQ_JK_JFQYL", "FQ_JK_JFQJY")"""
			cur.execute(sql1)
			conn.commit()
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def change_athena_status(environment, apply_id):
		"""修改Athena数据状态"""
		# noinspection PyGlobalUndefined
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""update sandbox_saas_athena.risk_apply set audit_result='APPROVE',quota=300000,step='COMPLETED',return_code=2000 where apply_id='{apply_id}';"""
			cur.execute(sql)
			conn.commit()
		except Exception as e:
			raise e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def change_repayment_plan_date(environment: str, period: int, date: str, project_id: int):
		"""修改还款计划天数"""
		assetId = GetSqlData.get_asset_id(environment, project_id)
		plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, assetId)
		try:
			conn = GetSqlData.conn_database(environment)
			cur = conn.cursor()
			sql = f"""
					update sandbox_saas.{plan_table}
					set plan_pay_date='{date}'
					where asset_id={assetId}
						and period={period}
						and repayment_status=1;
				"""
			cur.execute(sql)
			conn.commit()
		except Exception as e:
			conn.rollback()
			raise e
		finally:
			cur.close()
			conn.close()