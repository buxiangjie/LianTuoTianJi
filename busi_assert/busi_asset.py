# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 断言
"""
from assertpy import assert_that
from common.get_sql_data import GetSqlData
from busi_assert.info.extra_info import EntityInfo
from log.ulog import Ulog


class Asset:
	@staticmethod
	def check_column(info: str, environment: str, busi_id: str):
		map_dict = EntityInfo.mapping.get(info)
		busi_type = info.split("_")[1]
		sql_data = GetSqlData.select_extra_info(environment, busi_type, busi_id)
		for key, value in map_dict.items():
			Ulog.info(f"""校验参数:{key}是否落库""")
			assert_that(key in sql_data.keys()).is_true()
