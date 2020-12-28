# -*- coding: UTF-8 -*-
"""
@auth:buxiangjie
@date:2020-05-12 11:26:00
@describe: 
"""
bind = ["192.168.1.110:8817"]
workers = 2
daemon = True
reload = True
worker_class = "uvicorn.workers.UvicornH11Worker"
reload_engine = "auto"
preload_app = True