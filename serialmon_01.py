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
from http.server import BaseHTTPRequestHandler, HTTPServer
from serial import SerialException
import threading
import socket
import time
import sys

rel_state = 0

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
line = "$1;1;;2,1;2,2;3,3;4,4;5,5;6,6;7,7;8,8;9,9;10,1;11,2;12,3;13,4;14,5;15,6;16,7"
line = line.strip("$1;1;;")
values = (line.split(";"))
diff = [ "?", "?", "?", "?", "?", "?", "?", "?"]

#----------------------------[MyServer]
class RequestHandler(BaseHTTPRequestHandler):
    def resp_header(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def sendline(self, line):
        self.wfile.write(bytes(line, "utf-8"))

    def resp_page(self):
        global values
        global rel_state

        self.sendline("<html>")
        self.sendline("<head><title>home temperature observation</title></head>")
        self.sendline("<body><font face='verdana,arial'>")
        self.sendline("<table>")
        self.sendline("<tr><th>Raum</th><th>Temperatur</th><th>Luftfeuchtigkeit</th></tr>")
        self.sendline("<tr><td>Obergescho&szlig;</td><td>{:d}&deg;C</td><td>{:d}%</td></tr>".format(values[0], values[8]))
        self.sendline("<tr><td>Halle            </td><td>{:d}&deg;C</td><td>{:d}%</td></tr>".format(values[1], values[0]))
        self.sendline("<tr><td>Schlafzimmer     </td><td>{:d}&deg;C</td><td>{:d}%</td></tr>".format(values[2], values[10]))
        self.sendline("<tr><td>Toilette         </td><td>{:d}&deg;C</td><td>{:d}%</td></tr>".format(values[3], values[11]))
        self.sendline("<tr><td>Badezimmer       </td><td>{:d}&deg;C</td><td>{:d}%</td></tr>".format(values[4], values[12]))
        self.sendline("<tr><td>K&uuml;che       </td><td>{:d}&deg;C</td><td>{:d}%</td></tr>".format(values[5], values[13]))
        self.sendline("<tr><td>Heizung          </td><td>{:d}&deg;C</td><td>{:d}%</td></tr>".format(values[6], values[14]))
        self.sendline("<tr><td>B&uuml;ro        </td><td>{:d}&deg;C</td><td>{:d}%</td></tr>".format(values[7], values[15]))
        self.sendline("</table><p>")
        if rel_state == 1:
            self.sendline("Heizung ist ein<br>")
            self.sendline("<form action='' method='post'><button name='foo' value='upvote'>Heizung aus</button></form>")
        else:
            self.sendline("Heizung ist aus<br>")
            self.sendline("<form action='' method='post'><button name='foo' value='upvote'>Heizung ein</button></form>")
        self.sendline("</body>")

    def do_GET(self):
        log_info("<svr> do_GET")
        self.resp_header()
        self.resp_page()

    def do_POST(self):
        global rel_state

        log_info("<svr> do_POST")
        if rel_state == 1:
            rel_state = 0
        else:
            rel_state = 1
        self.resp_header()
        self.resp_page()
    
#----------------------------[serverthread]
def serverthread():
    global hsvr

    log_info("<svr> init")
    GPIO.output(svr_grn, GPIO.LOW)
    GPIO.output(svr_red, GPIO.HIGH)

    while True:
        try:
            hsvr = HTTPServer(("", 4711), RequestHandler)
            break
        except Exception:
            GPIO.output(svr_red, GPIO.LOW)
            time.sleep(0.5)            
            GPIO.output(svr_red, GPIO.HIGH)
            time.sleep(1)

    log_info("<svr> started")
    GPIO.output(svr_grn, GPIO.HIGH)
    GPIO.output(svr_red, GPIO.LOW)
    try:
        hsvr.serve_forever()
    except KeyboardInterrupt:
        hsvr.server_close()
    log_info("<svr> stop")
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
    global values

    message = """From: PI
    Subject: e-mail from pi

    Obergeschoß  {:>5s}°C {:>5s}%  {:s}
    Halle        {:>5s}°C {:>5s}%  {:s}
    Schlafzimmer {:>5s}°C {:>5s}%  {:s}
    Toilette     {:>5s}°C {:>5s}%  {:s}
    Badezimmer   {:>5s}°C {:>5s}%  {:s}
    Küche        {:>5s}°C {:>5s}%  {:s}
    Heizung      {:>5s}°C {:>5s}%  {:s}
    Büro         {:>5s}°C {:>5s}%  {:s}
    """.format(values[0], values[8], diff[0],
               values[1], values[9], diff[1],
               values[2], values[10], diff[2],
               values[3], values[11], diff[3],
               values[4], values[12], diff[4],
               values[5], values[13], diff[5],
               values[6], values[14], diff[6],
               values[7], values[15], diff[7])

    log_info("send: " + message)

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
        s = smtplib.SMTP(host, port)
        s.starttls()
        s.login(email, passw)
        s.sendmail(email, dest, message)
        s.quit()
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
    print("received: " + line)
    values = (line.split(";"))
    print("Obergeschoß  " + values[0] + "°C    " + values[ 8] + " %")
    print("Halle        " + values[1] + "°C    " + values[ 9] + " %")
    print("Schlafzimmer " + values[2] + "°C    " + values[10] + " %")
    print("Toilette     " + values[3] + "°C    " + values[11] + " %")
    print("Badezimmer   " + values[4] + "°C    " + values[12] + " %")
    print("Küche        " + values[5] + "°C    " + values[13] + " %")
    print("Heizung      " + values[6] + "°C    " + values[14] + " %")
    print("Büro         " + values[7] + "°C    " + values[15] + " %")
    return

#----------------------------[serial_init]
def serial_init():
    global ser
    global rel_out

    GPIO.output(led_grn, GPIO.LOW)
    GPIO.output(led_red, GPIO.HIGH)
    while True:
        line = "$1;1;;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?"
        schedule.run_pending()      # check clock

        if rel_state == 1:
            GPIO.output(rel_out, GPIO.HIGH)
        else:
            GPIO.output(rel_out, GPIO.LOW)

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
    global rel_state
    global hsvr

    GPIO.output(rel_out, GPIO.LOW)

    thread = threading.Thread(target=serverthread, args=[])
    thread.start()

    if len(sys.argv) == 2:
        if sys.argv[1] == "debug":
            time.sleep(2)
            run_test()
            hsvr.shutdown()
            log_info("exit (debug)")
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
        if rel_state == 1:
            GPIO.output(rel_out, GPIO.HIGH)
        else:
            GPIO.output(rel_out, GPIO.LOW)
   
#----------------------------[]     
if __name__=='__main__':
    global hsvr
    try:
        log_info("starting")
        main()
    except:
        GPIO.cleanup()
        hsvr.shutdown()
        log_info("exit")
    