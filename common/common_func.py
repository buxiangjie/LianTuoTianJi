#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from config.configer import Config
from log.logger import Logger
import requests,os

class Common():

	def __init__(self):
		self.url = Config().Get_Item("Testserver","url")
		self.logger = Logger(logger="Common").getlog()

	def Response(self,faceaddr,param=None):
		faceaddrs = Config().Get_Item("InterFaceAddr",faceaddr)
		url = self.url + faceaddrs
		header = {
			"Content-Type": "application/json",
			"Accept" : "application/json",
		}
		try:
			print("请求地址:%s"%url)
			print("请求参数:%s"%param)
			requests.post(url, data=param)
			return requests.post(url,data=param)
		except Exception as e:
			self.logger.error(e)