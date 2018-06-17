#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import dht22 as DHT
import time
import log

#----------------------------[writearray]
def writearray(array):
    try:
        with open("/usr/local/etc/serialmon_01.pic", 'wb') as fp:
            pickle.dump(array, fp)
        return
    except OSError:
        pass
    try:
        with open("serialmon_01.pic", 'wb') as fp:
            pickle.dump(array, fp)
        return
    except OSError:
        pass
    return

#----------------------------[main]
def main():
    array = [ "?", "?"]
    while True:
        humidity, temperature = DHT.read_retry(DHT.DHT22, 10)
        array[0] = str(humidity)
        array[1] = str(temperature)
        print (array)
        writearray(array)
        time.sleep(60)

#----------------------------[]
if __name__=='__main__':
    global hsvr
    try:
        log.info("dht", "starting")
        main()
    except:
        log.info("dht", "exit")
        pass
