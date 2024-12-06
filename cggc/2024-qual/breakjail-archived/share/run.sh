#!/bin/sh

exec 2>/dev/null
cd /home/pyjail
timeout 60 ./jail.py
