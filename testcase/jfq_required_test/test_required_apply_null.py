# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 
"""
import unittest
import os
import json
import ddt
from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config

logger = Logger(logger="jfq_required_project").getlog()


@ddt.ddt
class JfqPorjectNull(unittest.TestCase):
	file = Config().get_item('File', 'jfq_required_case_file')
	excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file
	excel_data = excel_table_byname(excel, 'apply_null')

	@classmethod
	def setUpClass(cls):
		cls.env = 'qa'
		cls.url = JfqPorject.excel_data[0]['url']
		cls.headers = JfqPorject.excel_data[0]['headers']
		cls.param = JfqPorject.excel_data[0]['param']

	def tearDown(self):
		pass

	@ddt.data(*excel_data)
	def test_project(self, data):
		print("接口名称:%s" % data['casename'])
		case = data['casename']
		param = json.loads(self.param)
		key = str(case).split("空")[1].split(".")[0]
		value = str(case).split("空")[1].split(".")[1]
		param[key][value] = None
		headers = json.loads(self.headers)
		rep = Common.response(
			faceaddr=self.url,
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product='cloudloan',
			environment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data['resultCode']))


@ddt.ddt
class JfqPorject(unittest.TestCase):
	file = Config().get_item('File', 'jfq_required_case_file')
	excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file
	excel_data = excel_table_byname(excel, 'apply_null')

	@classmethod
	def setUpClass(cls):
		cls.env = 'test'
		cls.url = JfqPorject.excel_data[0]['url']
		cls.headers = JfqPorject.excel_data[0]['headers']
		cls.param = JfqPorject.excel_data[0]['param']

	def tearDown(self):
		pass

	@ddt.data(*excel_data)
	def test_project(self, data):
		print("接口名称:%s" % data['casename'])
		case = data['casename']
		param = json.loads(self.param)
		key = str(case).split("空")[1].split(".")[0]
		value = str(case).split("空")[1].split(".")[1]
		del param[key][value]
		headers = json.loads(self.headers)
		rep = Common.response(
			faceaddr=self.url,
			headers=headers,
			data=json.dumps(param, ensure_ascii=False),
			product='cloudloan',
			environment=self.env
		)
		self.assertEqual(rep['resultCode'], int(data['resultCode']))


if __name__ == '__main__':
	unittest.main()
