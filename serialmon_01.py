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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

port = "/dev/ttyUSB0"
line = "$1;1;;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?"
line = line.replace("$1;1;;", "")
line = line.replace(',', '.')
values = line.split(";")
lval = values
diff = [ "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?"]
hcode = [ "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?"]

#----------------------------[gethtmltable]
def gethtmltable():
    global values
    global hcode
    global rel_state

    html  = "<table>"
    html += "<tr><th>Raum</th><th>Temperatur</th><th>Luftfeuchtigkeit</th></tr>"
    html += "<tr><td>Obergescho&szlig;</td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[0], hcode[0], values[ 8], hcode[ 8])
    html += "<tr><td>Halle            </td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[1], hcode[1], values[ 9], hcode[ 9])
    html += "<tr><td>Schlafzimmer     </td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[2], hcode[2], values[10], hcode[10])
    html += "<tr><td>Toilette         </td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[3], hcode[3], values[11], hcode[11])
    html += "<tr><td>Badezimmer       </td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[4], hcode[4], values[12], hcode[12])
    html += "<tr><td>K&uuml;che       </td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[5], hcode[5], values[13], hcode[13])
    html += "<tr><td>Heizung          </td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[6], hcode[6], values[14], hcode[14])
    html += "<tr><td>B&uuml;ro        </td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[7], hcode[7], values[15], hcode[15])
    html += "</table><p>"
    if rel_state == 1:
        html += "Heizung ist ein<br>"
    else:
        html += "Heizung ist aus<br>"
    return html

#----------------------------[MyServer]
class RequestHandler(BaseHTTPRequestHandler):
    def resp_header(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def senddata(self, data):
        self.wfile.write(bytes(data, "utf-8"))

    def resp_page(self):
        global rel_state

        self.senddata("<html>")
        self.senddata("<head><title>home temperature observation</title><meta http-equiv='refresh' content='5'></head>")
        self.senddata("<body><font face='verdana,arial'>")
        self.senddata("<p>{:s}</p>".format(time.strftime("%d-%m-%Y Time: %H:%M:%S",time.localtime())))
        self.senddata(gethtmltable())
        if rel_state == 1:
            self.senddata("<form action='' method='post'><button name='foo' value='upvote'>Heizung aus</button></form>")
        else:
            self.senddata("<form action='' method='post'><button name='foo' value='upvote'>Heizung ein</button></form>")
        self.senddata("</body>")

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

    # init server
    while True:
        try:
            hsvr = HTTPServer(("", 4711), RequestHandler)
            break
        except Exception:
            GPIO.output(svr_red, GPIO.LOW)
            time.sleep(0.5)            
            GPIO.output(svr_red, GPIO.HIGH)
            time.sleep(1)

    # running
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
    global diff

    # read config
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

    # email login
    try:
        s = smtplib.SMTP(host, port)
        s.starttls()
        s.login(email, passw)
    except Exception:
        log_info("SMTP error: " + traceback.format_exc())
        return

    # prepare email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "home temperature observation status"
    msg['From'] = email
    msg['To'] = dest

    html = """
    <head></head>
    <body>
        %s
    </body>
    """ % gethtmltable()
    msg.attach(MIMEText(html, 'html'))

    # send email
    try:
        s.sendmail(email, dest, msg.as_string())
        s.quit()
        log_info("email send")
    except Exception as e:
        log_info("SMTP error:" + e)

    return

#----------------------------[once_a_hour]
def once_a_hour():
    global line

    log_info("once_a_hour")
    log_line(line)
    return

#----------------------------[once_a_day]
def once_a_day():
    global lval
    global hcode
    global diff

    log_info("once_a_day")

    # calculate diff
    for i in range(16):
        if   values[i] == "?":
            diff[i] = "-"
            hcode[i] = "-"
        elif float(values[i]) > float(lval[i]):
            diff[i] = "▲"
            hcode[i] = "&#9652;"
        elif float(values[i]) < float(lval[i]):
            diff[i] = "▼"
            hcode[i] = "&#9662;"
        else:
            diff[i] = "●"
            hcode[i] = "&#9679;"
    lval = values

    # send mail
    send_mail()
    return

#----------------------------[analyze]
def analyze():
    global values
    global line
    global diff

    # format and split
    line = line.replace("$1;1;;", "")
    line = line.replace(',', '.')
    values = (line.split(";"))

    # output
    print(time.strftime("%d-%m-%Y Time: %H:%M:%S",time.localtime()))
    print("Obergeschoß  " + values[0] + "°C " + diff[0] + "   " + values[ 8] + " % " + diff[ 8])
    print("Halle        " + values[1] + "°C " + diff[1] + "   " + values[ 9] + " % " + diff[ 9])
    print("Schlafzimmer " + values[2] + "°C " + diff[2] + "   " + values[10] + " % " + diff[10])
    print("Toilette     " + values[3] + "°C " + diff[3] + "   " + values[11] + " % " + diff[11])
    print("Badezimmer   " + values[4] + "°C " + diff[4] + "   " + values[12] + " % " + diff[12])
    print("Küche        " + values[5] + "°C " + diff[5] + "   " + values[13] + " % " + diff[13])
    print("Heizung      " + values[6] + "°C " + diff[6] + "   " + values[14] + " % " + diff[14])
    print("Büro         " + values[7] + "°C " + diff[7] + "   " + values[15] + " % " + diff[15])
    return

#----------------------------[serial_init]
def serial_init():
    global ser
    global rel_out

    GPIO.output(led_grn, GPIO.LOW)
    GPIO.output(led_red, GPIO.HIGH)
    while True:
        schedule.run_pending()

        if rel_state == 1:
            GPIO.output(rel_out, GPIO.HIGH)
        else:
            GPIO.output(rel_out, GPIO.LOW)

        try:
            ser = serial.Serial(port,9600)
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
    global values
    global lval
    global rel_state
    global hsvr

    GPIO.output(rel_out, GPIO.LOW)

    thread = threading.Thread(target=serverthread, args=[])
    thread.start()

    # arguments
    if len(sys.argv) == 2:
        if sys.argv[1] == "debug":
            run_test()
            time.sleep(2)
            hsvr.shutdown()
            log_info("exit (debug)")
            GPIO.cleanup()
            return
        if sys.argv[1] == "fakeval":
            line = "$1;1;;10,1;20,2;30,3;40,4;50,5;60,6;70,7;80,8;90,9;10,1;11,2;12,3;13,4;14,5;15,6;16,7"
            line = line.replace("$1;1;;", "")
            line = line.replace(',', '.')
            values = line.split(";")
            lval = values
            lval[0] = "8.8"
            lval[1] = "22.5"
            analyze()
            once_a_hour()
            once_a_day()

    # init
    schedule.every().day.at("08:00").do(once_a_day)
    schedule.every().hour.do(once_a_hour)
    serial_init()

    # running
    while True:
        if not ser.isOpen():
            serial_init()
        schedule.run_pending()
        line = str(ser.readline(), "utf-8")
        analyze()
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
    