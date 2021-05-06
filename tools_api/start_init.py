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

Ulog().logger_().info("开始检查8817端口是否被占用")


if sys.platform in ("darwin", "linux"):
	port = os.popen("lsof -i:8817").read()
	if port == "":
		Ulog().logger_().info("端口未被占用")
	else:
		Ulog().logger_().info("进行端口清理操作-------------------------------------")
		data = port.strip(" ").replace(" ", "")
		Ulog().logger_().info(f"获取到的端口为:{data}")
		pid_list = re.findall('uvicorn(.*?)root', data)
		Ulog().logger_().info(f"匹配到的PID为:{pid_list}")
		count = 1
		for i in pid_list:
			Ulog().logger_().info(f"开始清理第{count}个端口-------------------------------------")
			os.popen(f"kill {str(i)}")
			Ulog().logger_().info(f"检查端口{i}是否被kill")
			pid = re.findall('uvicorn(.*?)root', str(os.popen("lsof -i:8817").read()).replace(" ", ""))
			Ulog().logger_().info(f"当前端口PID列表为:{pid}")
			if str(i) not in pid:
				Ulog().logger_().info("删除成功")
				count += 1
			else:
				Ulog.error("删除失败")
				raise Exception
