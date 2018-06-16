#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import dht22 as DHT
import time

#----------------------------[main]
def main():
    while True:
        humidity, temperature = DHT.read_retry(DHT.DHT22, 10)
        print (humidity)
        print (temperature)
        time.sleep(5)

#----------------------------[]
if __name__=='__main__':
    global hsvr
    try:
        main()
    except:
        pass
