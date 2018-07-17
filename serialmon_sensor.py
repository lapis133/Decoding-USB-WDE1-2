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

#----------------------------[ds1820]
def ds1820():
    try:
        file = open('/sys/devices/w1_bus_master1/w1_master_slaves')
        w1_slaves = file.readlines()
        file.close()
    except Exception:
        log.info("dht", "ds1820: access denied")
        return "?", "-"

    try:
        for line in w1_slaves:
            w1_slave = line.split("\n")[0]
            file = open('/sys/bus/w1/devices/' + str(w1_slave) + '/w1_slave')
            filecontent = file.read()
            file.close()

            stringvalue = filecontent.split("\n")[1].split(" ")[9]
            temperature = float(stringvalue[2:]) / 1000

            sval = "{:.1f}".format(temperature)
            print ("DS1820: " + sval)
            return sval, "-"

    except Exception:
        log.info("dht", "ds1820: device error")

    return "?", "-"

#----------------------------[main]
def main():
    array = [ "?", "?", "?", "?"]
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(status_led, GPIO.OUT)
    GPIO.output(status_led, GPIO.HIGH)
    while True:
        humidity, temperature = DHT.read_retry(DHT.DHT22, 10)
        array[0] = str(temperature)
        array[1] = str(humidity)
        array[2], array[3] = ds1820()
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
