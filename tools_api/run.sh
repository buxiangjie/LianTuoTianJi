#!/bin/bash
cd tools_api || exit
python3 start_init.py
uvicorn --host 192.168.9.229 --port 8817 main:app