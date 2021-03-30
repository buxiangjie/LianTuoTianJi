# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 
"""
import time
import asyncio
import aiomysql

from common.get_sql_data import GetSqlData
from common.common_func import Common
from typing import Optional
from log.ulog import Ulog


class ToolsSql(GetSqlData):

	@staticmethod
	async def conn_database(environment, source: Optional[str] = "saas"):
		"""
		数据库连接
		:param source: str
		:type environment:str
		"""
		yaml_data = Common.get_yaml_data("config", "database.yaml")
		config = yaml_data[environment][source]
		try:
			connect = await aiomysql.connect(**config)
			return connect
		except Exception as e:
			raise e

	@staticmethod
	async def exec_update(
			environment: str,
			sql: str,
			source: Optional[str] = "saas"
	):
		"""执行更新语句"""
		conn = None
		cur = None
		try:
			conn = await ToolsSql.conn_database(environment, source)
			cur = await conn.cursor()
			await cur.execute(sql)
			await conn.commit()
			Ulog.info(f"执行sql:{sql}")
		except Exception as e:
			await conn.rollback()
			raise e
		finally:
			await cur.close()
			conn.close()

	@staticmethod
	async def change_repayment_plan_date(environment: str, period: int, date: str, project_id: int):
		"""修改还款计划应还日期"""
		asid = GetSqlData.get_asset_id(environment, project_id)
		plan_table = 'repayment_plan_0' + GetSqlData.get_sub_table(environment, asid)
		sql = f"""
					update sandbox_saas.{plan_table}
					set plan_pay_date='{date}'
					where asset_id={asid}
						and period={period}
						and repayment_status=1;
				"""
		await ToolsSql.exec_update(environment, sql)

	@staticmethod
	async def del_asset_data(environment: str, asset_id: str):
		"""删除资产相关数据"""
		table_index = GetSqlData.get_sub_table(environment, asset_id)
		plan_table = 'repayment_plan_0' + table_index
		fee_table = 'fee_plan_0' + table_index
		rd_table = 'repayment_detail_0' + table_index
		od_table = 'overdue_detail_0' + table_index
		user_plan_table = 'user_repayment_plan_0' + table_index
		user_fee_table = 'user_fee_plan_0' + table_index
		user_rd_table = 'user_repayment_plan_0' + table_index
		sql1 = f"""delete from sandbox_saas.{plan_table} where asset_id={asset_id};"""
		sql2 = f"""delete from sandbox_saas.asset where id={asset_id};"""
		sql3 = f"""delete from sandbox_saas.asset_extra where asset_id={asset_id};"""
		sql4 = f"""delete from sandbox_saas.asset_fee where asset_id={asset_id};"""
		sql5 = f"""delete from sandbox_saas.asset_swap_apply where asset_id={asset_id};"""
		sql6 = f"""delete from sandbox_saas.asset_swap_detail where asset_id={asset_id};"""
		sql7 = f"""delete from sandbox_saas.overdue where asset_id={asset_id};"""
		sql8 = f"""delete from sandbox_saas.{fee_table} where asset_id={asset_id};"""
		sql9 = f"""delete from sandbox_saas.{rd_table} where asset_id={asset_id};"""
		sql10 = f"""delete from sandbox_saas.{od_table} where asset_id={asset_id};"""
		sql11 = f"""delete from sandbox_saas.repayment where asset_id={asset_id};"""
		sql12 = f"""delete from sandbox_saas.{user_fee_table} where asset_id={asset_id};"""
		sql13 = f"""delete from sandbox_saas.{user_plan_table} where asset_id={asset_id};"""
		sql14 = f"""delete from sandbox_saas.{user_rd_table} where asset_id={asset_id};"""
		sql_list = [sql1, sql2, sql3, sql4, sql5, sql6, sql7, sql8, sql9, sql10, sql11, sql12, sql13, sql14]
		for i in sql_list:
			await ToolsSql.exec_update(environment, i)
		return "执行完成"

	@staticmethod
	async def del_project_data(environment: str, projectid: int):
		"""删除进件相关数据"""
		sql1 = f"""delete from sandbox_saas.project_detail where id={projectid}"""
		sql2 = f"""delete from sandbox_saas.project_customer_detail where project_id={projectid}"""
		sql3 = f"""delete from sandbox_saas.project_enterprise_detail where project_id={projectid};"""
		sql4 = f"""delete from sandbox_saas.project_entity_detail where project_id={projectid};"""
		sql5 = f"""delete from sandbox_saas.project_extra_detail where project_id={projectid};"""
		sql_list = [sql1, sql2, sql3, sql4, sql5]
		for i in sql_list:
			await ToolsSql.exec_update(environment, i)
			print(time.ctime())
		return "执行完成"

	@staticmethod
	async def ss(x):
		Ulog.info(time.ctime())
		await asyncio.sleep(x)
		Ulog.info(f"""---{x}""")
		return "dddd"