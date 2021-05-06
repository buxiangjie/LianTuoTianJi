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

	# noinspection PyBroadException
	def __init__(self):
		self.logger = logger
		hand_list = []
		for key in self.logger._core.handlers:
			hand_list.append(key)
		if hand_list[-1] != 0:
			self.logger.remove(hand_list[-1])
		log_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)) + '/logs/')
		rq = '/' + time.strftime("%Y_%m_%d", time.localtime())
		if not os.path.exists(log_path):
			os.mkdir(log_path)
		self.logger.add(log_path + "/" + rq + ".log", rotation="00:00", enqueue=True)

	def logger_(self):
		return self.logger

# @staticmethod
# def info(msg):
# 	return logger.info(msg)
#
# @staticmethod
# def debug(msg):
# 	return logger.debug(msg)
#
# @staticmethod
# def warning(msg):
# 	return logger.warning(msg)
#
# @staticmethod
# def error(msg):
# 	return logger.error(msg)
