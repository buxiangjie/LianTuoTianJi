# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2020-05-12 16:00
@describe:卡卡贷进件接口字段必填项校验
"""
import unittest
import json
import ddt
import sys
from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config

logger = Logger(logger="kkd_apply").getlog()


@ddt.ddt
class KkdApply(unittest.TestCase):
	file = Config().get_item('File', 'kkd_required_case_file')
	excel_data = excel_table_byname(file, 'apply')

	@classmethod
	def setUpClass(cls):
		cls.env = sys.argv[3]
		cls.param = KkdApply.excel_data[0]['param']
		cls.headers = KkdApply.excel_data[0]['headers']
		cls.url = KkdApply.excel_data[0]['url']

	@ddt.data(*excel_data)
	def test_apply(self, data):
		print("接口名称:%s" % data['casename'])
		case = data['casename']
		param = json.loads(self.param)
		key = str(case).split("项")[1].split(".")[0]
		value = str(case).split("项")[1].split(".")[1]
		if value is '*':
			del param[key]
		else:
			del param[key][value]
		if len(self.headers) == 0:
			headers = None
		else:
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
