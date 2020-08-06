#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import unittest
import time
import sys
import smtplib
import os

import BeautifulReport as BeautifulReport

from HtmlRpeort.HTMLTestReportCN import HTMLTestRunner
from common.common_func import Common
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from log.logger import Logger
from config.configer import Config

logger = Logger(logger="run_all_case").getlog()


def all_case(dirs: str):
	"""批量添加用例到测试套件"""
	case_dir = Config().get_item(section="CaseFile", option=dirs)
	logger.info("用例执行文件夹%s" % case_dir)
	cases = unittest.TestSuite()
	discover = unittest.defaultTestLoader.discover(case_dir, pattern="test_*.py", top_level_dir=None)

	for test_suit in discover:
		for test_case in test_suit:
			cases.addTest(test_case)
	return cases


def send_report():
	"""
	使用smtp发送测试报告
	"""
	with open(globals()['filename'], 'rb') as f:
		mail_body = f.read()
	msg = MIMEMultipart()
	msg['From'] = 'bxj3416162@163.com'
	msg['To'] = 'buxiangjie@cloudloan.com'
	mails = Common.get_json_data('config', 'mail.json').get(sys.argv[1].split("_")[0])
	msg['Subject'] = Header(mails['Subject'][sys.argv[3]], 'utf8')
	msg['CC'] = mails['cc']

	msg_file = MIMEText(mail_body, 'base64', 'utf8')
	msg_file['Content-Type'] = 'application/octet-stream'
	msg_file["Content-Disposition"] = 'attachment;filename=report.html'
	msg.attach(msg_file)

	smtp = smtplib.SMTP('smtp.163.com')
	smtp.set_debuglevel(1)
	# smtp.login('924409272@qq.com', 'nrkquovrupcbbeej')  # 登录邮箱
	smtp.login('bxj3416162@163.com', '3416162zxc')  # 登录邮箱
	smtp.sendmail(msg['From'], (msg['To'].split(';') + msg['CC'].split(';')), msg.as_string())
	# smtp.sendmail(msg['From'], (msg['To'].split(';')), msg.as_string())
	smtp.quit()
	print('Report has send out!')


# def new_report(test_report: str) -> str:
# 	"""遍历出最新的测试报告"""
# 	# lists = os.listdir(test_report)  # 通过os.listdir函数遍历出该目录下所有文件
# 	# lists2 = sorted(lists)  # 按正序排列文件
# 	# file_new = os.path.join(test_report, lists2[-1])  # 找到正序排序的下面一个文件，即最新的文件
# 	return globals()['filename']


def begin(file: str):
	newtime = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
	if not os.path.exists("./test_report"):
		os.mkdir("test_report")
	globals()['filename'] = "./test_report/" + newtime + '.html'
	filename = newtime + ".html"
	fp = open(globals()['filename'], 'wb+')
	suit = all_case(file)
	# runner = HTMLTestRunner(stream=fp, title='小贷业务接口测试报告', description='执行情况')
	# runner.run(suit)
	result = BeautifulReport.BeautifulReport(suit)
	result.report(description="小贷业务接口报告", filename=filename, report_dir="test_report", theme="theme_candy")
	fp.close()


if __name__ == "__main__":
	begin(sys.argv[1])
	send_report()  # 调用发送报告函数
