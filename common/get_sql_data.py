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
from config.configer import Config
from log.logger import Logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger = Logger(logger="SqlData").getlog()


class GetSqlData(object):

	@staticmethod
	def conn_database(enviroment='python', source='saas'):
		"""
		数据库连接
		:param source: str
		:type enviroment:str
		"""
		global config, conn
		if enviroment == 'python':
			config = {
				'host': Config().get_item('Database', 'host'),
				'user': Config().get_item('Database', 'user'),
				'password': Config().get_item('Database', 'password'),
				'port': int(Config().get_item('Database', 'port')),
				'db': Config().get_item('Database', 'db'),
				'charset': 'utf8',
				'cursorclass': pymysql.cursors.DictCursor
			}
		elif enviroment == 'test':
			if source == 'saas':
				config = {
					'host': Config().get_item('test_database', 'host'),
					'user': Config().get_item('test_database', 'user'),
					'password': Config().get_item('test_database', 'password'),
					'port': int(Config().get_item('test_database', 'port')),
					'db': Config().get_item('test_database', 'db'),
					'charset': 'utf8',
					'cursorclass': pymysql.cursors.DictCursor
				}
			elif source == 'steamrunner':
				config = {
					'host': Config().get_item('test_database', 'host'),
					'user': Config().get_item('test_database', 'user'),
					'password': Config().get_item('test_database', 'password'),
					'port': int(Config().get_item('test_database', 'port')),
					'db': "sandbox_saas_steamrunner",
					'charset': 'utf8',
					'cursorclass': pymysql.cursors.DictCursor
				}
			else:
				config = {
					'host': Config().get_item('pay_test_database', 'host'),
					'user': Config().get_item('pay_test_database', 'user'),
					'password': Config().get_item('pay_test_database', 'password'),
					'port': int(Config().get_item('pay_test_database', 'port')),
					'db': Config().get_item('pay_test_database', 'db'),
					'charset': 'utf8',
					'cursorclass': pymysql.cursors.DictCursor
				}
		elif enviroment == 'qa':
			if source == 'saas':
				config = {
					'host': Config().get_item('qa_database', 'host'),
					'user': Config().get_item('qa_database', 'user'),
					'password': Config().get_item('qa_database', 'password'),
					'port': int(Config().get_item('qa_database', 'port')),
					'db': Config().get_item('qa_database', 'db'),
					'charset': 'utf8',
					'cursorclass': pymysql.cursors.DictCursor
				}
			elif source == 'steamrunner':
				config = {
					'host': Config().get_item('qa_database', 'host'),
					'user': Config().get_item('qa_database', 'user'),
					'password': Config().get_item('qa_database', 'password'),
					'port': int(Config().get_item('qa_database', 'port')),
					'db': 'sandbox_saas_steamrunner',
					'charset': 'utf8',
					'cursorclass': pymysql.cursors.DictCursor
				}
		elif enviroment == 'pay':
			config = {
				'host': Config().get_item('pay_test_database', 'host'),
				'user': Config().get_item('pay_test_database', 'user'),
				'password': Config().get_item('pay_test_database', 'password'),
				'port': int(Config().get_item('pay_test_database', 'port')),
				'db': Config().get_item('pay_test_database', 'db'),
				'charset': 'utf8',
				'cursorclass': pymysql.cursors.DictCursor
			}
		elif enviroment == 'prod':
			config = {
				'host': Config().get_item('prod_database', 'host'),
				'user': Config().get_item('prod_database', 'user'),
				'password': Config().get_item('prod_database', 'password'),
				'port': int(Config().get_item('prod_database', 'port')),
				'db': Config().get_item('prod_database', 'db'),
				'charset': 'utf8',
				'cursorclass': pymysql.cursors.DictCursor
			}
		try:
			conn = pymysql.connect(**config)
			# conn = mysql.connector.connect(**config)
			return conn
		except Exception as e:
			raise e

	@staticmethod
	def check_credit_step(enviroment: str, credit_id: str) -> str:
		"""
		检查授信步骤
		"""
		global conn, cur, sql
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f'''Select credit_step from sandbox_saas.credit where id = {credit_id};'''
			cur.execute(sql)
			msg = cur.fetchone().get('credit_step')
			cur.close()
			conn.close()
			return int(msg)
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def change_credit_step(enviroment: str, credit_id: str) -> str:
		"""修改罗马车贷/车置宝授信信息"""
		global cur, conn, sql
		conn = GetSqlData.conn_database(enviroment)
		try:
			cur = conn.cursor()
			sql = """
				UPDATE sandbox_saas_centaur.apply 
				set approve_status='3',ds_success='3',indicator='{}' WHERE apply_id=%s;
				""" % credit_id
			cur.execute(sql)
			conn.commit()
			cur.close()
			conn.close()
		except Exception as e:
			cur.close()
			conn.rollback()
			conn.close()
			raise e

	@staticmethod
	def change_jfx_credit_step(enviroment: str, user_id: str) -> str:
		"""修改牙医贷授信信息"""
		global cur, conn, sql
		conn = GetSqlData.conn_database(enviroment)
		try:
			cur = conn.cursor()
			sql = f"""
				UPDATE sandbox_saas_athena.risk_apply 
				set audit_result='APPROVE',quota='300000.00',level='1',step='COMPLETED' 
				WHERE user_id={user_id};
				"""
			cur.execute(sql)
			conn.commit()
			cur.close()
			conn.close()
		except Exception as e:
			cur.close()
			conn.rollback()
			conn.close()
			raise e

	@staticmethod
	def change_credit_status(enviroment: str, credit_id: str) -> str:
		"""修改授信表状态与步骤"""
		global cur, conn, sql
		conn = GetSqlData.conn_database(enviroment)
		try:
			cur = conn.cursor()
			create_time = Common.get_not_now_time("before", "minutes", 10)
			# sql = f"""
			# 	UPDATE sandbox_saas.credit
			# 	set credit_status=1,credit_step=4,audit_result='APPROVE',
			# 	audit_amount=300000,tot_amount=300000,available_amount=300000
			# 	WHERE id={credit_id};
			# 	"""
			sql = f"""update sandbox_saas.credit set create_time='{create_time}' where id='{credit_id}';"""
			cur.execute(sql)
			conn.commit()
			cur.close()
			conn.close()
		except Exception as e:
			cur.close()
			conn.rollback()
			conn.close()
			raise e

	@staticmethod
	def credit_set(enviroment: str, credit_id: str) -> str:
		"""授信时调用，根据环境判断是否需要等待补偿"""
		global step
		print("开始检查授信步骤")
		if Config().get_item("Switch", "credit") == "1":
			# GetSqlData.change_credit_step(enviroment, credit_id)
			GetSqlData.change_credit_status(enviroment, credit_id)
			GetSqlData.change_athena_status(enviroment, credit_id)
		status = 2
		version = 1
		while status != 4:
			if version > 10:
				print("授信未成功")
				break
			step = GetSqlData().check_credit_step(enviroment, credit_id)
			if step != 4:
				print(f"当前授信步骤为:{step:d};当前循环次数为:{version:d}")
				version += 1
				time.sleep(10)
			elif step == 4:
				print("当前授信已完成,可以进行下个步骤!")
				status = 4

	@staticmethod
	def check_loan_result(enviroment: str, project_id: str) -> str:
		"""查询放款状态"""
		global cur, conn, sql
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f'''Select loan_result from sandbox_saas.project_detail where id = {project_id};'''
			cur.execute(sql)
			msg = cur.fetchone().get('loan_result')
			cur.close()
			conn.close()
			return msg
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def loan_set(enviroment: str, project_id: str) -> str:
		"""放款申请后调用，查询放款状态是否成功"""
		global res
		print("开始检查放款步骤")
		time.sleep(4)
		if GetSqlData().check_loan_result(enviroment, project_id) == -1:
			print("放款状态不正确，未申请放款成功")
		else:
			try:
				version = 1
				while GetSqlData().check_loan_result(enviroment, project_id) != 1:
					if version > 100:
						print(f"循环{version - 1}次未查询到放款成功状态，判断为放款失败")
						break
					res = GetSqlData().check_loan_result(enviroment, project_id)
					if res == 0:
						print(f"当前loan_result为:{res};放款失败")
						break
					if res != 1:
						print(f"当前loan_result为:{res};当前循环次数为:{version}")
						version += 1
						time.sleep(10)
			except Exception as e:
				raise e

	@staticmethod
	def change_pay_status(enviroment: str, project_id: str):
		"""修改steamrunner.pay_order的放款状态为成功"""
		global cur, conn, sql
		finish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		if Config().get_item("Switch", "loan") == '1':
			print("放款开关已关闭，走虚拟放款逻辑")
			time.sleep(5)
			try:
				conn = GetSqlData.conn_database(enviroment, source='steamrunner')
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
				cur.close()
				conn.close()
				raise e
		else:
			print("放款开关已开启,走真实放款流程")

	@staticmethod
	def get_asset_id(enviroment: str, project_id: str) -> str:
		"""获取资产id"""
		global cur, conn, sql
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f"""select id from sandbox_saas.asset WHERE project_id='{project_id}';"""
			cur.execute(sql)
			msg = cur.fetchone().get("id")
			cur.close()
			conn.close()
			return msg
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def get_user_repayment_detail(project_id, enviroment, period, repayment_plan_type, feecategory=2002) -> dict:
		"""
		获取用户还款计划中的关联：
		渠道计划id
		计划还款时间
		剩余应还金额
		:rtype:
		"""
		global cur, conn, plan_table, sql
		try:
			asset_id = GetSqlData.get_asset_id(enviroment, project_id)
			if repayment_plan_type in ["1", "2"]:
				if enviroment == 'test':
					plan_table = 'user_repayment_plan_0' + str((asset_id % 8 + 1))
				elif enviroment == 'qa':
					plan_table = 'user_repayment_plan_0' + str((asset_id >> 22) % 8 + 1)
				conn = GetSqlData.conn_database(enviroment)
				cur = conn.cursor()
				sql = f"""
					select * from {plan_table} 
					where asset_id = {str(asset_id)} 
					and period = {str(period)} 
					and repayment_plan_type = {str(repayment_plan_type)};
					"""
				cur.execute(sql)
				msg = cur.fetchone()
				cur.close()
				conn.close()
				return msg
			elif feecategory == 3003:
				if enviroment == 'test':
					plan_table = 'user_fee_plan_0' + str((asset_id % 8 + 1))
				elif enviroment == 'qa':
					plan_table = 'user_fee_plan_0' + str((asset_id >> 22) % 8 + 1)
				conn = GetSqlData.conn_database(enviroment)
				cur = conn.cursor()
				sql = f"""
					select * from {plan_table} 
					where asset_id = {str(asset_id)} 
					and period = {str(period)} and fee_category = {str(repayment_plan_type)};
					"""
				cur.execute(sql)
				msg = cur.fetchone()
				cur.close()
				conn.close()
				return msg
			else:
				if enviroment == 'test':
					plan_table = 'fee_plan_0' + str((asset_id % 8 + 1))
				elif enviroment == 'qa':
					plan_table = 'fee_plan_0' + str((asset_id >> 22) % 8 + 1)
				conn = GetSqlData.conn_database(enviroment)
				cur = conn.cursor()
				sql = f"""
					select plan_pay_date,rest_amount,cur_amount,source_plan_id from {plan_table} 
					where asset_id = {str(asset_id)} and period = {str(period)} and fee_category = {feecategory};
					"""
				cur.execute(sql)
				msg = cur.fetchone()
				cur.close()
				conn.close()
				return msg
		except Exception as e:
			raise e

	@staticmethod
	def get_user_repayment_amount(project_id: str, enviroment: str, period: str) -> str:
		"""获取用户还款计划当期应还款总额"""
		global cur, conn, plan_table, sql
		try:
			asset_id = GetSqlData.get_asset_id(enviroment, project_id)
			if enviroment == 'test':
				plan_table = 'user_repayment_plan_0' + str((asset_id % 8 + 1))
			elif enviroment == 'qa':
				plan_table = 'user_repayment_plan_0' + str((asset_id >> 22) % 8 + 1)
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f"""
				select sum(cur_amount) as cur_amount from {plan_table} 
				where asset_id={str(asset_id)} and period={str(period)};
				"""
			cur.execute(sql)
			amount = cur.fetchone().get('cur_amount')
			cur.close()
			conn.close()
			return float(amount)
		except Exception as e:
			raise e

	@staticmethod
	def get_repayment_amount(project_id: str, enviroment: str, period: str) -> str:
		"""获取机构还款计划当期应还款总额"""
		global cur, conn, plan_table, sql
		try:
			asset_id = GetSqlData.get_asset_id(enviroment, project_id)
			if enviroment == 'test':
				plan_table = 'repayment_plan_0' + str((asset_id % 8 + 1))
			elif enviroment == 'qa':
				plan_table = 'repayment_plan_0' + str((asset_id >> 22) % 8 + 1)
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f"""
				select sum(cur_amount) as amount from {plan_table} 
				where asset_id={str(asset_id)} and period={str(period)};
				"""
			cur.execute(sql)
			amount = cur.fetchone().get("amount")
			cur.close()
			conn.close()
			return float(amount)
		except Exception as e:
			raise e

	@staticmethod
	def get_all_repayment_amount(project_id: str, enviroment: str) -> str:
		"""获取资产还款金额"""
		global cur, conn, sql
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f"""select amount from sandbox_saas.asset where project_id='{project_id}';"""
			cur.execute(sql)
			amount = cur.fetchone().get('amount')
			cur.close()
			conn.close()
			return float(amount)
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def get_maturity(project_id: str, enviroment: str) -> str:
		"""获取资产期数"""
		global cur, conn, sql
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f'''select maturity from sandbox_saas.asset where project_id="{project_id}";'''
			cur.execute(sql)
			maturity = cur.fetchone().get("maturity")
			cur.close()
			conn.close()
			return maturity
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def get_repayment_principal(project_id: str, enviroment: str, period: str) -> str:
		"""获取机构还款计划应还本金"""
		global cur, conn, plan_table, sql
		try:
			asset_id = GetSqlData.get_asset_id(enviroment, project_id)
			if enviroment == 'test' or enviroment == 'dev':
				plan_table = 'repayment_plan_0' + str((asset_id % 8 + 1))
			elif enviroment == 'qa':
				plan_table = 'repayment_plan_0' + str((asset_id >> 22) % 8 + 1)
			conn = GetSqlData.conn_database(enviroment)
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
			cur.close()
			conn.close()
			return str(amount)
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def get_debt_amount(project_id, enviroment):
		"""获取资产剩余应还本金"""
		global cur, conn, sql
		try:
			asset_id = GetSqlData.get_asset_id(enviroment, project_id)
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f"""select debt_amount from sandbox_saas.asset where id={asset_id}"""
			cur.execute(sql)
			debt = cur.fetchone().get('debt_amount')
			cur.close()
			conn.close()
			return debt
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def get_repayment_detail(project_id: str, enviroment: str, period: str, repayment_plan_type: str) -> dict:
		"""
				获取机构还款计划中的关联：
				渠道计划id
				计划还款时间
				剩余应还金额
				:rtype: object
				"""
		global cur, conn, plan_table, sql
		try:
			asset_id = GetSqlData.get_asset_id(enviroment, project_id)
			if enviroment == 'test':
				plan_table = 'repayment_plan_0' + str((asset_id % 8 + 1))
			elif enviroment == 'qa':
				plan_table = 'repayment_plan_0' + str((asset_id >> 22) % 8 + 1)
			conn = GetSqlData.conn_database(enviroment)
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
			cur.close()
			conn.close()
			return msg
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def check_user_amount(user_id, enviroment):
		"""持续查询用户可用额度"""
		version = 1
		while True:
			if version > 10:
				print(f'''当前查询次数{version}''')
				break
			user_amount = GetSqlData.user_amount(user_id, enviroment)
			if user_amount > 0.00:
				print("额度检查完成")
				break
			elif user_amount == 0.000000:
				version += 1
				time.sleep(5)

	@staticmethod
	def user_amount(user_id, enviroment):
		"""查询用户可用额度"""
		global cur, conn, sql, availableAmount
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f'select available_amount from sandbox_saas_nebula.amount where user_id={user_id};'
			cur.execute(sql)
			available_amount = cur.fetchone().get('available_amount')
			cur.close()
			conn.close()
			return available_amount
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def project_audit_status(project_id: str, enviroment: str) -> int:
		"""查询进件审核状态"""
		global cur, conn, sql, audit_status
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f'select audit_status from sandbox_saas.project_detail where id={project_id};'
			cur.execute(sql)
			audit_status = cur.fetchone().get('audit_status')
			cur.close()
			conn.close()
			return audit_status
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def project_result(project_id: str, enviroment: str) -> str:
		"""进件审核结果查询"""
		print("开始检查进件审核步骤")
		try:
			version = 1
			while True:
				if version > 10:
					print(f"{version}次未查询到进件审核成功状态")
					break
				audit_status = GetSqlData().project_audit_status(project_id, enviroment)
				if audit_status != 2:
					print(f"当前进件审核状态为:{audit_status};当前查询次数为:{version}")
					version += 1
					time.sleep(10)
				elif audit_status == 2:
					print("进件审核成功")
					break
		except Exception as e:
			raise e

	@staticmethod
	def change_project_audit_status(project_id: str, enviroment: str) -> str:
		"""修改进件审核状态为通过"""
		global cur, conn, sql
		if Config().get_item("Switch", "project") == '1':
			print("风控已关闭，走虚拟进件风控逻辑")
			try:
				conn = GetSqlData.conn_database(enviroment)
				cur = conn.cursor()
				sql = f'update sandbox_saas.project_detail set audit_status=2,audit_result=1,project_step=5 where id={project_id};'
				cur.execute(sql)
				conn.commit()
				cur.close()
				conn.close()
				return "修改进件状态为审核通过"
			except Exception as e:
				cur.close()
				conn.close()
				raise e
		else:
			print("风控开关已开启，走真实风控流程")
			GetSqlData.project_result(project_id, enviroment)

	@staticmethod
	def check_project_audit_status(project_id: str, enviroment: str) -> int:
		"""查询进件审核状态"""
		global cur, conn, sql
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f'select audit_status from sandbox_saas.project_detail where id={project_id};'
			cur.execute(sql)
			conn.commit()
			audit_status = cur.fetchone().get('audit_status')
			cur.close()
			conn.close()
			return audit_status
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def loan_sql(env):
		"""修改steamrunner放款状态"""
		global cur, conn, sql
		try:
			conn = GetSqlData.conn_database(env)
			cur = conn.cursor()
			sql = f"""update sandbox_saas_steamrunner.sr_pay_order 
					set code=2000 where 
					project_id in
					(select id from sandbox_saas.project_detail 
					where product_code in
					("XJ_JFX_YYDSIN","XJ_JFX_YYDMUL","FQ_RM_RMYM","XJ_ROMA_CAR","XJ_ROMA_CARV2","XJ_DX_SYJV2","XJ_DX_SYJ"));"""
			cur.execute(sql)
			conn.commit()
			cur.close()
			conn.close()
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def select_asset():
		"""查询牙医贷、任买没有放款的资产数量"""
		global cur, conn, sql
		try:
			conn = GetSqlData.conn_database("qa")
			cur = conn.cursor()
			sql = f"""select count(*) as c 
					from sandbox_saas.project_detail 
					where  product_code in("XJ_JFX_YYDSIN","XJ_JFX_YYDMUL","FQ_RM_RMYM") 
					and loan_result=2;
					"""
			cur.execute(sql)
			conn.commit()
			coun = cur.fetchone().get("c")
			cur.close()
			conn.close()
			return coun
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def get_current_period(project_id, enviroment):
		"""获取资产当前发生期"""
		global cur, conn, plan_table, sql
		try:
			asset_id = GetSqlData.get_asset_id(enviroment, project_id)
			if enviroment == 'test':
				plan_table = 'repayment_plan_0' + str((asset_id % 8 + 1))
			elif enviroment == 'qa':
				plan_table = 'repayment_plan_0' + str((asset_id >> 22) % 8 + 1)
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f"""select period 
					from sandbox_saas.{plan_table} 
					where asset_id={asset_id} 
					and repayment_status=1 
					order by period limit 1
					"""
			cur.execute(sql)
			period = cur.fetchone().get('period')
			cur.close()
			conn.close()
			return period
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def get_prod_project_id(asset_id):
		"""获取进件ID"""
		global conn, cur, sql
		try:
			conn = GetSqlData.conn_database('prod')
			cur = conn.cursor()
			sql = f"""select project_id from saas_zhtb where asset_id={asset_id}"""
			cur.execute(sql)
			project_id = cur.fetchone()[0]
			cur.close()
			conn.close()
			return project_id
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def get_contact_id(project_id):
		"""获取合同ID"""
		global conn, cur, sql
		try:
			conn = GetSqlData.conn_database('prod')
			cur = conn.cursor()
			sql = f"""select id from saas_zhtb where association_id={project_id}"""
			cur.execute(sql)
			contact_id = cur.fetchone()[0]
			cur.close()
			conn.close()
			return contact_id
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def like_asset_id(asset_id, enviroment):
		"""资产ID模糊查询"""
		global conn, cur, sql
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f"""select id from asset where id like '{asset_id}';"""
			cur.execute(sql)
			asset_id = cur.fetchone().get('id')
			cur.close()
			conn.close()
			return asset_id
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def asset_count(enviroment):
		"""查询资产ID"""
		global conn, cur, sql
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = "select id from asset;"
			cur.execute(sql)
			asset_id = cur.fetchall()
			cur.close()
			conn.close()
			ids = []
			for i in asset_id:
				ids.append(i.get('id'))
			return ids
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def repayment_plan(asset_id: str, enviroment: str) -> int:
		"""查询机构还款计划条数"""
		global conn, cur, sql, plan_table
		try:
			conn = GetSqlData.conn_database(enviroment)
			if enviroment == 'test':
				plan_table = 'repayment_plan_0' + str((asset_id % 8 + 1))
			elif enviroment == 'qa':
				plan_table = 'repayment_plan_0' + str((asset_id >> 22) % 8 + 1)
			cur = conn.cursor()
			sql = f"""select count(*) as c from {plan_table} where asset_id={asset_id};"""
			cur.execute(sql)
			count = cur.fetchone().get('c')
			cur.close()
			conn.close()
			return int(count)
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def select_need_audit_project_ids() -> list:
		"""
		查询要修改审核状态的进件ID
		用于Job
		"""
		global conn, cur, sql
		try:
			conn = GetSqlData.conn_database("qa")
			cur = conn.cursor()
			sql = f"""select id from project_detail where product_code in ("FQ_JK_JFQYL", "FQ_JK_JFQJY") and audit_status !=2"""
			cur.execute(sql)
			ids = cur.fetchall()
			cur.close()
			conn.close()
			idss = []
			for i in ids:
				idss.append(i.get("id"))
			return idss
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def change_audit():
		"""
		修改进件审核状态
		用于Job
		"""
		global conn, cur, sql
		try:
			conn = GetSqlData.conn_database("qa")
			cur = conn.cursor()
			sql = f"""update project_detail set audit_status=2,audit_result=1 where product_code in ("FQ_JK_JFQYL", "FQ_JK_JFQJY")"""
			cur.execute(sql)
			conn.commit()
			cur.close()
			conn.close()
		except Exception as e:
			cur.close()
			conn.close()
			raise e

	@staticmethod
	def change_athena_status(enviroment, apply_id):
		"""修改Athena数据状态"""
		global conn, cur, sql
		try:
			conn = GetSqlData.conn_database(enviroment)
			cur = conn.cursor()
			sql = f"""update sandbox_saas_athena.risk_apply set audit_result='APPROVE',quota=300000,step='COMPLETED',return_code=2000 where apply_id='{apply_id}';"""
			cur.execute(sql)
			conn.commit()
			cur.close()
			conn.close()
		except Exception as e:
			cur.close()
			conn.close()
			raise e
