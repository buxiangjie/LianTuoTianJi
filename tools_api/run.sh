#!/bin/bash
sudo -s
python3 start_init.py
gunicorn -c gun_config.py main:app