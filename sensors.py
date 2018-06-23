#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import socket
import time
import log

array = [ "?", "?", "?", "?"]
sflag = False

#----------------------------[read]
def read():
    return array

#----------------------------[sensordata]
def sensordata(data):
    global array
    log.info("sensor", "received: " + data)
    try:
        if data[:10] == "serialmon;":
            xarr = data.split(";")
            if len(xarr) == 5:
                xarr.remove("serialmon")
                array = list(xarr)
    except Exception:
        pass
    return

#----------------------------[sensorthread]
def sensorthread():
    log.info("sensor", "init")
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("", 4712))
            s.settimeout(1)
            s.listen(1)
            break
        except Exception:
            if sflag == True:
                log.info("sensor", "stop")
                return
            log.info("sensor", "init error")
            time.sleep(5)

    log.info("sensor", "started")
    while True:
        try:
            conn, addr = s.accept()
            conn.settimeout(1)
            log.info("sensor", "connection accepted " + str(addr))
            while True:
                try:
                    data = str(conn.recv(128), "utf-8")
                    if not data: break
                    sensordata(data)
                except socket.timeout:
                    if sflag == True:
                        conn.close()
                        s.close()
                        log.info("sensor", "stop")
                        return
            conn.close()
            log.info("sensor", "connection closed")
        except socket.timeout:
            if sflag == True:
                s.close()
                log.info("sensor", "stop")
                return
    return

#----------------------------[stop]
def stop():
    global sflag
    sflag = 1
    return

#----------------------------[start]
def start():
    thread = threading.Thread(target=sensorthread, args=[])
    thread.start()
    return
