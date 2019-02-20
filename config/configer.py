#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import configparser,os

class Config():
	"""配置文件常用功能封装"""
	def __init__(self):
		self.cf = configparser.ConfigParser()
		self.cf.read(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config/config.ini")

	"""获取参数值"""
	def Get_Item(self,section,option):
		return self.cf.get(section,option)

	"""修改参数值"""
	def Set_Item(self,section,option,value=None):
		try:
			self.cf.set(section,option,value)
			with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config/config.ini", "w+") as f:
				self.cf.write(f)
			f.close()
			return "修改成功"
		except Exception as e:
			return str(e)

	"""添加参数"""
	def Add_Section(self,section):
		try:
			self.cf.add_section(section)
			with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config/config.ini", "w+") as f:
				self.cf.write(f)
			f.close()
			return "添加成功"
		except Exception as e:
			return str(e)