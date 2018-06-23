#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import dht22 as DHT
import time
import log
import gpio as GPIO

status_led = 37

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
    array = [ "?", "?", "?", "?"]
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(status_led, GPIO.OUT)
    GPIO.output(status_led, GPIO.HIGH)
    while True:
        humidity, temperature = DHT.read_retry(DHT.DHT22, 10)
        #humidity = 47.123456
        #temperature = 26.123456
        array[0] = str(temperature)
        array[1] = str(humidity)
        print (array)
        writearray(array)
        time.sleep(60)
        GPIO.output(status_led, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(status_led, GPIO.HIGH)

#----------------------------[]
if __name__=='__main__':
    global hsvr
    try:
        log.info("dht", "starting")
        main()
    except:
        GPIO.cleanup()
        log.info("dht", "exit")
        pass
