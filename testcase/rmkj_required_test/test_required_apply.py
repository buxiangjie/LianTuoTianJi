# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2019-10-24 16:00
@describe:任买医美进件接口字段必填项校验
"""
import unittest
import os
import json
import ddt
import sys
from common.common_func import Common
from common.open_excel import excel_table_byname
from config.configer import Config


@ddt.ddt
class Apply(unittest.TestCase):
	file = Config().get_item('File', 'rmkj_required_case_file')
	excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file
	excel_data = excel_table_byname(excel, 'apply')

	def setUp(self):
		self.env = sys.argv[3]

	def tearDown(self):
		pass

	@ddt.data(*excel_data)
	def test_apply(self, data):
		print("接口名称:%s" % data['casename'])
		param = json.loads(data['param'])
		headers = json.loads(data['headers'])
		rep = Common.response(
			faceaddr=data['url'],
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product='cloudloan',
			environment=self.env
		)
		self.assertEqual(int(rep['resultCode']), data['resultCode'])


if __name__ == '__main__':
	unittest.main()
