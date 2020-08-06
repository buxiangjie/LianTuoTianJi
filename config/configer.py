#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import configparser
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Config(object):
    """配置文件常用功能封装"""

    def __init__(self):
        self.cf = configparser.ConfigParser()
        self.cf.read(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config/config.ini",
                     encoding='utf-8')

    """获取参数值"""

    def get_item(self, section: str, option: str) -> str:
        return self.cf.get(section, option)

    """修改参数值"""

    def set_item(self, section: str, option: str, value=None) -> str:
        try:
            self.cf.set(section, option, value)
            with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config/config.ini", "w+",
                      encoding='utf-8') as f:
                self.cf.write(f)
            f.close()
            return "修改成功"
        except Exception as e:
            raise e

    """添加参数"""

    def add_section(self, section: str) -> str:
        try:
            self.cf.add_section(section)
            with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config/config.ini", "w+",
                      encoding='utf-8') as f:
                self.cf.write(f)
            f.close()
            return "添加成功"
        except Exception as e:
            raise e
