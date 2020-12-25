# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 
"""

import os, sys
from log.ulog import Ulog

logger = Ulog().getlog()

logger.info("开始检查8817端口是否被占用")

port = None
if sys.platform == "darwin":
	port = os.popen("lsof -i:8817").read()
	if port is None:
		logger.info("端口未被占用")
	else:
		os.popen("kill")
elif sys.platform == "win32":
	port = os.popen("").read()
	if port is None:
		logger.info("端口未被占用")
	else:
		pass