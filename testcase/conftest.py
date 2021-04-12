# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 
"""

import allure
import pytest

from common.common_func import Common


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

@pytest.fixture(scope="session")
@allure.step("生成redis随机参数")
def red(env):
	return Common.p2p_get_userinfo(environment=env, frame="pytest")