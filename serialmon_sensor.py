#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dht22 as DHT
import time
import log
import gpio as GPIO
import socket

status_led = 37

#----------------------------[senddata]
def senddata(array):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("127.0.0.1", 4712))
    except Exception:
        log.info("dht", "connection failed")
        return
    data = "serialmon;{:s};{:s};{:s};{:s}".format(array[0], array[1], array[2], array[3])
    s.send(data.encode("utf-8"))
    s.close()
    return

#----------------------------[main]
def main():
    array = [ "?", "?", "?", "?"]
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(status_led, GPIO.OUT)
    GPIO.output(status_led, GPIO.HIGH)
    while True:
        humidity, temperature = DHT.read_retry(DHT.DHT22, 10)
        humidity = 47.123456
        temperature = 26.123456
        array[0] = str(temperature)
        array[1] = str(humidity)
        print (array)
        senddata(array)
        for i in range (12):
            time.sleep(5)
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
