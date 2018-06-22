#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle

try:
    from Adafruit_DHT import *
except ImportError:
    #----------------------------[DHT22]
    def DHT22():
        return

    #----------------------------[read_retry]
    def read_retry(sensor, pin):
        return 0, 0

#----------------------------[read]
def read():
    array = [ "?", "?"]
    try:
        with open ("/usr/local/etc/serialmon_01.pic", 'rb') as fp:
            array = pickle.load(fp)
        return array
    except Exception:
        pass

    try:
        with open ("serialmon_01.pic", 'rb') as fp:
            array = pickle.load(fp)
        return array
    except Exception:
        pass

    return array
