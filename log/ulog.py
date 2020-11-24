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
	def __init__(self):
		log_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)) + '/logs/')
		rq = '/' + time.strftime("%Y_%m_%d", time.localtime())
		if not os.path.exists(log_path):
			os.mkdir(log_path)
		logger.add(log_path + "/" + rq +".log", rotation="00:00")

	def getlog(self):
		return logger