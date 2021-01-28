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

# 把当前目录的父目录加到sys.path中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


def pytest_addoption(parser):
	parser.addoption("--env", default="test", help="environment")


@pytest.fixture(scope="session")
@allure.step("接收外部参数判断运行环境")
def env(request):
	return request.config.getoption("--env")


@pytest.fixture(scope="session")
@allure.step("连接与环境对应的Redis")
def r(env):
	return Common.conn_redis(env)
