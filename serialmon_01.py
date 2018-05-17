#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import RPi.GPIO as GPIO
except ImportError:
    import gpio as GPIO
import schedule
import smtplib
import serial
from serial import SerialException
import time
import sys
import os

led_grn = 12
led_red = 16

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_grn, GPIO.OUT)
GPIO.setup(led_red, GPIO.OUT)

port = '/dev/ttyUSB0'     # serial port of USB-WDE1
server = smtplib.SMTP(os.environ.get('SERIALMON_SMPT_HOST'), os.environ.get('SERIALMON_SMPT_PORT'))
values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

#----------------------------[send_mail]
def send_mail():
    message = """Subject: e-mail from pi

    %s
    """ % (values)
    server.login(os.environ.get('SERIALMON_SMPT_EMAIL'), os.environ.get('SERIALMON_SMPT_PASSWORD'))
    server.sendmail(os.environ.get('SERIALMON_SMPT_EMAIL'), os.environ.get('SERIALMON_DESTINATION_EMAIL'), message)
    server.quit()
    return

#----------------------------[once_a_day]
def once_a_day():
    print ("once_a_day")
    send_mail()
    return

#----------------------------[analyze]
def analyze(line):
    global values
    line = line.strip("$1;1;;")
    print (line)
    values = (line.split(";"))
    print ("Obergesch " + values[0] + "°C    " + values[ 8] + " %")
    print ("Halle     " + values[1] + "°C    " + values[ 9] + " %")
    print ("Schlafzi  " + values[2] + "°C    " + values[10] + " %")
    print ("Toilette  " + values[3] + "°C    " + values[11] + " %")
    print ("Badezi    " + values[4] + "°C    " + values[12] + " %")
    print ("Kueche    " + values[5] + "°C    " + values[13] + " %")
    print ("Heizung   " + values[6] + "°C    " + values[14] + " %")
    print ("Buero     " + values[7] + "°C    " + values[15] + " %")
    return

#----------------------------[serial_init]
def serial_init():
    global ser
    GPIO.output(led_grn, GPIO.LOW)
    GPIO.output(led_red, GPIO.HIGH)
    while True:
        try:
            ser = serial.Serial(port,9600)  # open serial line        
            print ("connected: " + port)
            GPIO.output(led_grn, GPIO.HIGH)
            GPIO.output(led_red, GPIO.LOW)
            return
        except SerialException:
            print ("Unable to open serial port %s") % port
            GPIO.output(led_red, GPIO.LOW)
            time.sleep(0.5)            
            GPIO.output(led_red, GPIO.HIGH)
            time.sleep(5)

#----------------------------[run_test]
def run_test():
    line = "$1;1;;30;31;32;33;34;35;36;37;50;51;52;53;54;55;56;57"
    analyze(line)
    once_a_day()

#----------------------------[main]
def main():
    global ser

    if len(sys.argv) == 2:
        if sys.argv[1] == "debug":
            run_test()
            GPIO.cleanup()
            return

    schedule.every().day.at("08:00").do(once_a_day)
    serial_init()

    while True:
        if not ser.isOpen():
            serial_init()
        schedule.run_pending()      # check clock
        line = ser.readline()       # read line from WDE1
        analyze(line)               # analyze
        GPIO.output(led_grn, GPIO.LOW0)
        time.sleep(0.5)            
        GPIO.output(led_grn, GPIO.HIGH)
   
#----------------------------[]     
if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
    