# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 
"""
import os
import time

from loguru import logger


class Ulog:
	"""
	初始化日志输出目录与规则
	"""
	log_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)) + '/logs/')
	rq = '/' + time.strftime("%Y_%m_%d", time.localtime())
	if not os.path.exists(log_path):
		os.mkdir(log_path)
	logger.add(log_path + "/" + rq + ".log", rotation="00:00")

	@staticmethod
	def info(msg):
		return logger.info(msg)

	@staticmethod
	def debug(msg):
		return logger.debug(msg)

	@staticmethod
	def warning(msg):
		return logger.warning(msg)

	@staticmethod
	def error(msg):
		return logger.error(msg)
