#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

#----------------------------[info]
def info(module, info):
    print("[" + module + "] " + info)
    try:
        f = open("/var/log/serialmon_info.log","a")
    except PermissionError:
        f = open("serialmon_info.log","a")
    f.write(time.strftime("%Y-%m-%d %H:%M:%S") + ": [" + module + "] " + info + "\r\n")
    f.close()
    return

#----------------------------[line]
def line(line):
    try:
        f = open("/var/log/serialmon_01.log","a")
    except PermissionError:
        f = open("serialmon_01.log","a")
    f.write(time.strftime("%d.%m.%Y %H:00") + ";" + line + "\r\n")
    f.close()
    return