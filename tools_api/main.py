# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-10-18 13:37:00
@describe: 
"""
import sys
import os
import uvicorn

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from tools_api import saas

app = FastAPI(title="测试", description="测试")

app.include_router(saas.router, prefix="/saas", tags=["saas"])

# if __name__ == '__main__':
# 	uvicorn.run(
# 		"main:app",
# 		log_level="info",
# 		reload=True,
# 		host="localhost",
# 		port=8817
# 	)
