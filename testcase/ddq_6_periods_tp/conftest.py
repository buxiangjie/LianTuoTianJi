# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 
"""

import allure
import pytest
import sys
import os

from common.common_func import Common
from config.configer import Config

# 把当前目录的父目录加到sys.path中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


@pytest.fixture(scope="session")
@allure.step("定义excel文件路径")
def excel():
	file = Config().get_item('File', 'yzf_case_file')
	excel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + file
	return excel
