# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2020-02-05 15:38
@describe:新罗马授信接口字段为null校验
"""
import unittest
import os
import json
import ddt
import sys
from common.common_func import Common
from common.open_excel import excel_table_byname
from config.configer import Config

# 把当前目录的父目录加到sys.path中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


@ddt.ddt
class RomaCreditApplyNull(unittest.TestCase):
	file = Config().get_item('File', 'new_roma_required_case_file')
	excel_data = excel_table_byname(file, 'credit_apply_data_null')
	param = excel_data[0]['param']
	url = excel_data[0]['url']
	headers = excel_data[0]['headers']
	env = "test"

	@ddt.data(*excel_data)
	def test_credit_apply(self, data):
		case = data['casename']
		param = json.loads(self.param)
		key = str(case).split("空")[1].split(".")[0]
		value = str(case).split("空")[1].split(".")[1]
		if "List" in key:
			param[key][0][value] = None
		elif "已婚" in str(case).split("空")[0]:
			param['personal']['maritalStatus'] = 1
			param[key][value] = None
		elif "无合同" in str(case).split("空")[0]:
			param['orderDetail']['isHasContract'] = 'N'
			param[key][value] = None
		elif "无企业" in str(case).split("空")[0]:
			param['orderDetail']['hasCompany'] = 'N'
			param[key][value] = None
		else:
			param[key][value] = None
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
