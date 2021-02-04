# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 
"""
from common.get_sql_data import GetSqlData


class ToolsSql(GetSqlData):

	@staticmethod
	def change_repayment_plan_date(environment: str, period: int, date: str, project_id: int):
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
		GetSqlData.exec_update(environment, sql)

	@staticmethod
	def del_asset_data(environment: str, asset_id: int):
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
			GetSqlData.exec_update(environment, i)
		return "执行完成"

	@staticmethod
	def del_project_data(environment: str, projectid: int):
		"""删除进件相关数据"""
		sql1 = f"""delete from sandbox_saas.project_detail where id={projectid}"""
		sql2 = f"""delete from sandbox_saas.project_customer_detail where project_id={projectid}"""
		sql3 = f"""delete from sandbox_saas.project_enterprise_detail where project_id={projectid};"""
		sql4 = f"""delete from sandbox_saas.project_entity_detail where project_id={projectid};"""
		sql5 = f"""delete from sandbox_saas.project_extra_detail where project_id={projectid};"""
		sql_list = [sql1, sql2, sql3, sql4, sql5]
		for i in sql_list:
			GetSqlData.exec_update(environment, i)
		return "执行完成"
