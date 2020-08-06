#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import xlrd


def open_excel(file):
    """
    :param file: 文件路径
    :return:An instance of the :class:`~xlrd.book.Book` class.
    """
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(str(e))


def excel_table_byname(file, by_name, colnameindex=0) -> list:
    """
    :param file: 文件路径
    :param by_name: 表sheet页的名称
    :param colnameindex: 表头列名所在行的索引
    """
    data = open_excel(file)  # 打开文件
    table = data.sheet_by_name(by_name)  # 通过名称获取sheet页面数据
    nrows = table.nrows  # 列数
    colnames = table.row_values(colnameindex)  # 第colnameindex行数据
    list = []  # 准备一个空列表放数据
    for rownum in range(1, nrows):  # for循环  由于0是标题，所以循环从1开始
        row = table.row_values(rownum)  # row等于rownum行的值
        if row:
            app = {}  # 定义一个空数组
            for i in range(len(colnames)):  # 循环
                app[colnames[i]] = row[i]  # 当i有长度时，app数组里面第i行等于row的第i行的值
            list.append(app)  # 把app的值添加到列表中
    return list
