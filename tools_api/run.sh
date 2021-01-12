#!/bin/bash

spawn sudo su
expect "Password:"
send "cd /tools_api\r"
send "111111\r"
send "python3 start_init.py\r"
send "/home/buxj/.local/bin/uvicorn main:app\r"

expect eof
