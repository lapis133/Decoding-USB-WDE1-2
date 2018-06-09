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
import threading
import socket
import time
import sys

stop_thread = False;

rel_out = 7
led_grn = 12
led_red = 16
svr_red = 32
svr_grn = 36

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_grn, GPIO.OUT)
GPIO.setup(led_red, GPIO.OUT)
GPIO.setup(svr_grn, GPIO.OUT)
GPIO.setup(svr_red, GPIO.OUT)
GPIO.setup(rel_out, GPIO.OUT)

port = '/dev/ttyUSB0'     # serial port of USB-WDE1
values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
line = "$1;1;;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?"

#----------------------------[showtime]
def showtime():
    global lt
    lt = time.localtime()
    print (time.strftime("%d,%m,%Y Time: %H,%M,%S",lt))
    print()
    return

#----------------------------[clientdata]
def clientdata(data):
    if data == "rel_out=1":
        log_info("<svr> rel_out=1")
        GPIO.output(rel_out, GPIO.HIGH)
    elif data == "rel_out=0":
        log_info("<svr> rel_out=0")
        GPIO.output(rel_out, GPIO.LOW)
    else:
        log_info("<svr> data: " + data)
    return

#----------------------------[serverthread]
def serverthread():
    log_info("<svr> init")
    GPIO.output(svr_grn, GPIO.LOW)
    GPIO.output(svr_red, GPIO.HIGH)
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("", 4711))
            s.settimeout(1)
            s.listen(1)
            GPIO.output(svr_grn, GPIO.HIGH)
            GPIO.output(svr_red, GPIO.LOW)
            break
        except Exception:
            if stop_thread == True:
                log_info("<svr> stop")
                return
            GPIO.output(svr_red, GPIO.LOW)
            time.sleep(0.5)            
            GPIO.output(svr_red, GPIO.HIGH)
            time.sleep(5)

    log_info("<svr> started")
    while True:
        try:
            conn, addr = s.accept()
            conn.settimeout(1)
            log_info("<svr> connection accepted " + str(addr))
            while True:
                try:
                    data = str(conn.recv(20), "utf-8")
                    if not data: break
                    clientdata(data)
                except socket.timeout:
                    GPIO.output(svr_grn, GPIO.LOW)
                    time.sleep(0.5)            
                    GPIO.output(svr_grn, GPIO.HIGH)
                    if stop_thread == True:
                        conn.close()
                        s.close()
                        log_info("<svr> stop")
                        return
            conn.close()
            log_info("<svr> connection closed")
        except socket.timeout:
            if stop_thread == True:
                s.close()
                log_info("<svr> stop")
                return
    return

#----------------------------[log_info]
def log_info(info):
    print("[log] " + info)
    try:
        f = open("/var/log/serialmon_info.log","a")
    except PermissionError:
        f = open("serialmon_info.log","a")
    f.write(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + info + "\r\n")
    f.close()
    return

#----------------------------[log_line]
def log_line(line):
    try:
        f = open("/var/log/serialmon_01.log","a")
    except PermissionError:
        f = open("serialmon_01.log","a")
    f.write(time.strftime("%d.%m.%Y %H:00") + ";" + line + "\r\n")
    f.close()
    return

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
        log_info("serialmon_01.ini not filled")
        return
    try:
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(email, passw)
        server.sendmail(email, dest, message)
        server.quit()
        log_info("email send")
    except Exception:
        log_info("SMTP error")
        return
    return

#----------------------------[once_a_hour]
def once_a_hour():
    global line

    log_info("once_a_hour")
    line = line.strip("$1;1;;")
    log_line(line)
    return

#----------------------------[once_a_day]
def once_a_day():
    log_info("once_a_day")
    send_mail()
    return

#----------------------------[analyze]
def analyze():
    global values
    global line

    line = line.strip("$1;1;;")
   # print("received: " + line)
    values = (line.split(";"))
    showtime()
    print("Obergeschoß  " + values[0] + " °C    " + values[ 8] + " %")
    print("Halle        " + values[1] + " °C    " + values[ 9] + " %")
    print("Schlafzimmer " + values[2] + " °C    " + values[10] + " %")
    print("Toilette     " + values[3] + " °C    " + values[11] + " %")
    print("Badezimmer   " + values[4] + " °C    " + values[12] + " %")
    print("Küche        " + values[5] + " °C    " + values[13] + " %")
    print("Heizung      " + values[6] + " °C    " + values[14] + " %")
    print("Büro         " + values[7] + " °C    " + values[15] + " %")
    print()
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
            log_info("connected: " + port)
            GPIO.output(led_grn, GPIO.HIGH)
            GPIO.output(led_red, GPIO.LOW)
            return
        except SerialException:
            print ("[dbg] unable to connect")
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

    GPIO.output(rel_out, GPIO.LOW)

    if len(sys.argv) == 2:
        if sys.argv[1] == "debug":
            run_test()
            log_info("exit (debug)")
            GPIO.cleanup()
            return

    thread = threading.Thread(target=serverthread, args=[])
    thread.start()

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
        log_info("starting")
        main()
    except:
        stop_thread = True
        log_info("exit")
        GPIO.cleanup()
    