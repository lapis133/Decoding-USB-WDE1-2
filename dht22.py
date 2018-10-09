#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from Adafruit_DHT import *
except ImportError:
    #----------------------------[DHT22]
    def DHT22():
        return

    #----------------------------[read_retry]
    def read_retry(sensor, pin):
        return 0, 0
