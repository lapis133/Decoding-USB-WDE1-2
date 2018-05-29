#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import RPi.GPIO as GPIO
except ImportError:
    import gpio as GPIO
import configparser
import datetime
import schedule
import smtplib
import serial
from serial import SerialException
import time
import sys

led_grn = 12
led_red = 16

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_grn, GPIO.OUT)
GPIO.setup(led_red, GPIO.OUT)

port = '/dev/ttyUSB0'     # serial port of USB-WDE1
values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
line = "$1;1;;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?"

#----------------------------[send_mail]
def send_mail():
    message = """Subject: e-mail from pi

    %s
    """ % (values)

    config = configparser.ConfigParser()
    config.read('/usr/local/etc/serialmon_01.ini')
    try:
        host  = config["EMAIL"]["SMPT_HOST"]
        port  = config["EMAIL"]["SMPT_PORT"]
        email = config["EMAIL"]["SMPT_EMAIL"]
        passw = config["EMAIL"]["SMPT_PASSWORD"]
        dest  = config["EMAIL"]["DESTINATION_EMAIL"]
    except KeyError:
        print ("serialmon_01.ini not filled")
        return
    try:
        server = smtplib.SMTP(host, port)
        server.login(email, passw)
        server.sendmail(email, dest, message)
        server.quit()
    except Exception:
        print ("SMTP error")
        return
        
    return

#----------------------------[once_a_hour]
def once_a_hour():
    global line

    print ("once_a_hour")
    try:
        fobj_out = open("/var/log/serialmon_01.log","a")
    except PermissionError:
        fobj_out = open("serialmon_01.log","a")
    line = line.strip("$1;1;;")
    fobj_out.write(time.strftime("%d.%m.%Y %H:00") + ";" + line + "\r\n")
    fobj_out.close()
    return

#----------------------------[once_a_day]
def once_a_day():
    print ("once_a_day")
    send_mail()
    return

#----------------------------[analyze]
def analyze():
    global values
    global line

    line = line.strip("$1;1;;")
    print (line)
    values = (line.split(";"))
    print ("Obergeschoß  " + values[0] + "°C    " + values[ 8] + " %")
    print ("Halle        " + values[1] + "°C    " + values[ 9] + " %")
    print ("Schlafzimmer " + values[2] + "°C    " + values[10] + " %")
    print ("Toilette     " + values[3] + "°C    " + values[11] + " %")
    print ("Badezimmer   " + values[4] + "°C    " + values[12] + " %")
    print ("Küche        " + values[5] + "°C    " + values[13] + " %")
    print ("Heizung      " + values[6] + "°C    " + values[14] + " %")
    print ("Büro         " + values[7] + "°C    " + values[15] + " %")
    return

#----------------------------[serial_init]
def serial_init():
    global ser
    GPIO.output(led_grn, GPIO.LOW)
    GPIO.output(led_red, GPIO.HIGH)
    while True:
        line = "$1;1;;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?"
        schedule.run_pending()      # check clock
        try:
            ser = serial.Serial(port,9600)  # open serial line        
            print ("connected: " + port)
            GPIO.output(led_grn, GPIO.HIGH)
            GPIO.output(led_red, GPIO.LOW)
            return
        except SerialException:
            print ("Unable to open serial port " + port)
            GPIO.output(led_red, GPIO.LOW)
            time.sleep(0.5)            
            GPIO.output(led_red, GPIO.HIGH)
            time.sleep(5)

#----------------------------[run_test]
def run_test():
    analyze()
    once_a_hour()
    once_a_day()

#----------------------------[main]
def main():
    global ser
    global line

    if len(sys.argv) == 2:
        if sys.argv[1] == "debug":
            run_test()
            GPIO.cleanup()
            return

    schedule.every().day.at("08:00").do(once_a_day)
    schedule.every().hour.do(once_a_hour)    
    serial_init()

    while True:
        if not ser.isOpen():
            serial_init()
        schedule.run_pending()              # check clock
        line = str(ser.readline(), "utf-8") # read line from WDE1
        analyze()                           # analyze
        GPIO.output(led_grn, GPIO.LOW)
        time.sleep(0.5)            
        GPIO.output(led_grn, GPIO.HIGH)
   
#----------------------------[]     
if __name__=='__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        GPIO.cleanup()
    