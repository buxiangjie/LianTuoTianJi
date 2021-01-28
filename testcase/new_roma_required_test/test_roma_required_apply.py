# -*- coding: UTF-8 -*-
"""
@auth:bxj
@date:2020-01-14 15:38
@describe:新罗马授信接口字段必填项校验
"""
import unittest
import json
import ddt

from common.common_func import Common
from log.logger import Logger
from common.open_excel import excel_table_byname
from config.configer import Config

logger = Logger(logger="roma_credit_apply").getlog()


@ddt.ddt
class RomaCreditApply(unittest.TestCase):
	file = Config().get_item('File', 'new_roma_required_case_file')
	excel_data = excel_table_byname(file, 'credit_apply_data_new')
	param = excel_data[0]['param']
	url = excel_data[0]['url']
	headers = excel_data[0]['headers']
	env = 'test'

	@ddt.data(*excel_data)
	def test_credit_apply(self, data):
		print("接口名称:%s" % data['casename'])
		case = data['casename']
		param = json.loads(self.param)
		key = str(case).split("项")[1].split(".")[0]
		value = str(case).split("项")[1].split(".")[1]
		aim = 0
		if value is '*':
			del param[key]
		else:
			if "List" in key:
				aim = 1
			if "已婚" in str(case).split("项")[0]:
				param['personal']['maritalStatus'] = 1
			if "无合同" in str(case).split("项")[0]:
				param['orderDetail']['isHasContract'] = 'N'
			if "无企业" in str(case).split("项")[0]:
				param['orderDetail']['hasCompany'] = 'N'
			if aim != 1:
				print(f'key:{key};value:{value}')
				del param[key][value]
			else:
				del param[key][0][value]
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
