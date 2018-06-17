#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gpio as GPIO
import log
import datetime
import schedule
import serial
import mail
from http.server import BaseHTTPRequestHandler, HTTPServer
from serial import SerialException
import pickle
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

line   = "$1;1;;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?"
values = ["?"] * 16
lval   = list(values) # last vulues
diff   = list(values) # diffs
hcode  = list(values) # html diff

#----------------------------[readdht22]
def readdht22():
    array = [ "?", "?"]
    try:
        with open ("/usr/local/etc/serialmon_01.pic", 'rb') as fp:
            array = pickle.load(fp)
        try:
            os.remove("/usr/local/etc/serialmon_01.pic")
        except OSError:
            pass
        return array
    except Exception:
        pass

    try:
        with open ("serialmon_01.pic", 'rb') as fp:
            array = pickle.load(fp)
        try:
            os.remove("serialmon_01.pic")
        except OSError:
            pass
        return array
    except Exception:
        pass

    return array

#----------------------------[gethtmltable]
def gethtmltable():
    global values
    global hcode
    global rel_state

    html  = "<table>"
    html += "<tr align='left'><th>Raum</th><th>Temperatur&nbsp;&nbsp;</th><th>Luftfeuchtigkeit</th></tr>"
    html += "<tr><td>Obergescho&szlig;&nbsp;&nbsp</td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[0], hcode[0], values[ 8], hcode[ 8])
    html += "<tr><td>Halle            &nbsp;&nbsp</td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[1], hcode[1], values[ 9], hcode[ 9])
    html += "<tr><td>Schlafzimmer     &nbsp;&nbsp</td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[2], hcode[2], values[10], hcode[10])
    html += "<tr><td>Toilette         &nbsp;&nbsp</td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[3], hcode[3], values[11], hcode[11])
    html += "<tr><td>Badezimmer       &nbsp;&nbsp</td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[4], hcode[4], values[12], hcode[12])
    html += "<tr><td>K&uuml;che       &nbsp;&nbsp</td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[5], hcode[5], values[13], hcode[13])
    html += "<tr><td>Heizung          &nbsp;&nbsp</td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[6], hcode[6], values[14], hcode[14])
    html += "<tr><td>B&uuml;ro        &nbsp;&nbsp</td><td>{:s} &deg;C {:s}</td><td>{:s} % {:s}</td></tr>".format(values[7], hcode[7], values[15], hcode[15])
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
        log.info("svr", "do_GET")
        self.resp_header()
        self.resp_page()

    def do_POST(self):
        global rel_state

        log.info("svr", "do_POST")
        if rel_state == 1:
            rel_state = 0
        else:
            rel_state = 1
        self.resp_header()
        self.resp_page()

#----------------------------[serverthread]
def serverthread():
    global hsvr

    log.info("svr", "init")
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
    log.info("svr", "started")
    GPIO.output(svr_grn, GPIO.HIGH)
    GPIO.output(svr_red, GPIO.LOW)
    try:
        hsvr.serve_forever()
    except KeyboardInterrupt:
        hsvr.server_close()
    log.info("svr", "stop")
    return

#----------------------------[once_a_hour]
def once_a_hour():
    global line

    log.info("main", "once_a_hour")
    log.line(line)
    return

#----------------------------[once_a_day]
def once_a_day():
    global lval
    global hcode
    global diff
    global values

    log.info("main", "once_a_day")

    # calculate diff
    for i in range(16):
        if lval[i] == "?":
            lval[i] = values[i]

        if   values[i] == "?":
            diff[i] = "-"
            hcode[i] = "-"
        elif float(values[i]) > float(lval[i]):
            diff[i] = "▲"
            hcode[i] = "&#9650;"
        elif float(values[i]) < float(lval[i]):
            diff[i] = "▼"
            hcode[i] = "&#9660;"
        else:
            diff[i] = "●"
            hcode[i] = "&#9679;"
    lval = list(values)

    # send mail
    mail.send(gethtmltable())
    return

#----------------------------[analyze]
def analyze():
    global values
    global line
    global diff

    # readdht
    dht22 = readdht22()

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
            ser = serial.Serial("/dev/ttyUSB0", 9600)
            log.info("serial", "usb connected")
            GPIO.output(led_grn, GPIO.HIGH)
            GPIO.output(led_red, GPIO.LOW)
            return
        except SerialException:
            GPIO.output(led_red, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(led_red, GPIO.HIGH)
            time.sleep(5)

#----------------------------[run_test]
def run_test():
    global line
    global lval

    dht22 = readdht22()
    print (dht22)

    # check line with ?
    analyze()
    once_a_hour()
    once_a_day()
    # check received line
    line = "$1;1;;10,1;20,2;30,3;40,4;50,5;60,6;70,7;80,8;90,9;10,1;11,2;12,3;13,4;14,5;15,6;16,7"
    analyze()
    once_a_hour()
    once_a_day()
    # check diffs
    lval = list(values)
    lval[0] = "8.8"
    lval[1] = "22.5"
    once_a_hour()
    once_a_day()
    analyze()
    return

#----------------------------[main]
def main():
    global ser
    global line
    global values
    global lval
    global rel_state
    global hsvr

    GPIO.output(rel_out, GPIO.LOW)

    mail.send(gethtmltable())

    thread = threading.Thread(target=serverthread, args=[])
    thread.start()

    # arguments
    if len(sys.argv) == 2:
        if sys.argv[1] == "debug":
            run_test()
            time.sleep(2)
            hsvr.shutdown()
            log.info("main", "exit (debug)")
            GPIO.cleanup()
            return
        if sys.argv[1] == "fakeval":
            line = "$1;1;;10,1;20,2;30,3;40,4;50,5;60,6;70,7;80,8;90,9;10,1;11,2;12,3;13,4;14,5;15,6;16,7"
            analyze()
            lval = list(values)
            lval[0] = "8.8"
            lval[1] = "22.5"
            once_a_hour()
            once_a_day()
            analyze()

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
        log.info("main", "starting")
        main()
    except:
        GPIO.cleanup()
        try:
            hsvr.shutdown()
        except:
            pass
        log.info("main", "exit")
