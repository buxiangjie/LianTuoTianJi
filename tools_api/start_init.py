# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 
"""

import os, sys, re
print(sys.path)
print(os.path.curdir)
print(sys.version)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from log.ulog import Ulog

logger = Ulog().getlog()

logger.info("开始检查8817端口是否被占用")


if sys.platform in ("darwin", "linux"):
	port = os.popen("lsof -i:8817").read()
	if port == "":
		logger.info("端口未被占用")
	else:
		logger.info("进行端口清理操作-------------------------------------")
		data = port.strip(" ").replace(" ", "")
		logger.info(f"获取到的端口为:{data}")
		pid_list = re.findall('Python(.*?)boxiangjie', data)
		logger.info(f"匹配到的PID为:{pid_list}")
		count = 1
		for i in pid_list:
			logger.info(f"开始清理第{count}个端口-------------------------------------")
			os.popen(f"kill {str(i)}")
			logger.info(f"检查端口{i}是否被kill")
			pid = re.findall('Python(.*?)boxiangjie', str(os.popen("lsof -i:8817").read()).replace(" ", ""))
			logger.info(f"当前端口PID列表为:{pid}")
			if str(i) not in pid:
				logger.info("删除成功")
				count += 1
			else:
				logger.error("删除失败")
				raise Exception
