# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-10-18 13:37:00
@describe: 
"""
import uvicorn
import sys
import os
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from pydantic import BaseModel
from dateutil.relativedelta import relativedelta
from datetime import date
from typing import Optional
from common.get_sql_data import GetSqlData
from common.common_func import Common


app = FastAPI(title="测试接口")


class OverdueItem(BaseModel):
	enviroment: str
	project_id: Optional[int] = None
	period: int
	start_date: Optional[date] = None

@app.post("/overdue/change", name="修改还款计划为逾期")
def change_overdue(item: OverdueItem):
	pers = list(range(1,item.period+1))
	count = item.period
	for per in pers:
		if item.start_date:
			date = str(item.start_date - relativedelta(months=count)).split(" ")[0]
		else:
			date = str(datetime.datetime.now() - relativedelta(months=count)).split(" ")[0]
		print(date)
		print(item)
		GetSqlData.change_repayment_plan_date(item.enviroment,per,date,item.project_id)
		count -= 1

if __name__ == '__main__':
	uvicorn.run(app="main:app", host="192.168.1.108", port=8817, reload=True)