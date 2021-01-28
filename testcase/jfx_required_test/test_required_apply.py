# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2019-08-23 09:28
@describe:牙医贷授信接口字段必填项校验
"""
import unittest
import os
import json
import ddt
import sys
from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config

logger = Logger(logger="credit_apply").getlog()


@ddt.ddt
class CreditApply(unittest.TestCase):
	file = Config().get_item('File', 'jfx_required_case_file')
	excel_data = excel_table_byname(file, 'credit_apply_data')
	env = 'qa'

	@ddt.data(*excel_data)
	def test_credit_apply(self, data):
		print("接口名称:%s" % data['casename'])
		param = json.loads(data['param'])
		if len(data['headers']) == 0:
			headers = None
		else:
			headers = json.loads(data['headers'])
		rep = Common.response(
			faceaddr=data['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product="cloudloan",
			environment=self.env
		)
		self.assertEqual(str(json.loads(rep.text)['resultCode']), data['resultCode'])


if __name__ == '__main__':
	unittest.main()
