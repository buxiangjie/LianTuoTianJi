#!/bin/bash

spawn su root
expect "Password:"
send "111111\r"
send "cd /tools_api\r"
send "python3 start_init.py\r"
send "gunicorn -c gun_confg.py main:app\r"

expect eof
exit