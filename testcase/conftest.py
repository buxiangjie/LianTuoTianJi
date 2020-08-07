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


def pytest_addoption(parser):
	parser.addoption("--env", default="test", help="script run enviroment")
	parser.addoption("--types", default="-")


@pytest.fixture(scope="session")
def env(request):
	return request.config.getoption("--env")


@pytest.fixture(scope="session")
def types(request):
	return request.config.getoption("--types")


@pytest.fixture(scope="session")
def r(env):
	return Common.conn_redis(env)