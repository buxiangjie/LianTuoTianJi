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
	# if item.asset_id:
	# 	assetId = item.asset_id
	# elif item.project_id:
		# assetId = GetSqlData.get_asset_id(enviroment=item.enviroment, project_id=item.project_id)
	# else:
		# return {"code": 5000, "error":"project_id和asset_id必须有一个!"}
	pers = list(range(1,item.period))
	count = item.period
	for per in pers:
		date = str(datetime.datetime.now() - relativedelta(months=count)).split(" ")[0]
		GetSqlData.change_repayment_plan_date(item.enviroment,per,date,item.project_id)

if __name__ == '__main__':
	uvicorn.run(app="main:app", host="192.168.1.115", port=8817, reload=True)