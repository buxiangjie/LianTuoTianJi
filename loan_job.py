# -*- coding: UTF-8 -*-
"""
@auth:
@date:
@describe:
"""
import schedule
import threading
import time
import random
from common.get_sql_data import GetSqlData


def loan_job():
    try:
        GetSqlData.loan_sql()
        print(f"执行完成,任务编号为{str(random.random()).split('.')[1]}")
    except Exception as e:
        print(e)


def thread_loan_job():
    threading.Thread(target=loan_job).start()


if __name__ == '__main__':
    schedule.every(1).minutes.do(thread_loan_job)
    while True:
        schedule.run_pending()
        time.sleep(60)
