# -*- coding: UTF-8 -*-
"""
@auth:
@date:
@describe:
"""
from common.open_excel import excel_table_byname
from common.get_sql_data import GetSqlData
import os


def get_period(asset_id):
    global cur, conn
    try:
        conn = GetSqlData.conn_database("prod")
        cur = conn.cursor()
        sql = f'''select period from saas_zhtb.asset_swap_detail where asset_id={asset_id} and repayment_plan_type=1 order by period desc limit 1;'''
        cur.execute(sql)
        period = cur.fetchone()[0]
        cur.close()
        conn.close()
        return period
    except Exception as e:
        return str(e)


def vs_period(asset_id):
    global cur, conn
    try:
        conn = GetSqlData.conn_database("prod")
        cur = conn.cursor()
        sql = f'''select maturity,current_channel,current_vendor from saas_zhtb.asset where id={asset_id};'''
        cur.execute(sql)
        res = cur.fetchall()[0]
        maturity = res[0]
        current_channel = res[1]
        current_vendor = res[2]
        rese = [maturity, current_channel, current_vendor]
        cur.close()
        conn.close()
        return rese
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    dea = excel_table_byname(f'{os.path.dirname(os.path.abspath(__file__))}/data/11.xlsx', 'Sheet1')
    cc = []
    dd = []
    for a in dea:
        cc.append(a['资产id'])
    for i in cc:
        per = get_period(i)
        per2 = vs_period(i)
        if per == per2[0] and ((per2[1] and per2[2]) == 1):
            print("*" * 50)
        else:
            print(f'资产:{i}异常')
            dd.append(i)
    print(dd)
