#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import schedule
import serial
from serial import SerialException
import time
import sys
# own modules
import gpio as GPIO
import dht22 as DHT
import webserver
import mail
import log

rel_state = 0

line   = "$1;1;;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?"
values = ["?"] * (16+2)
lval   = list(values) # last vulues
diff   = list(values) # diffs
hcode  = list(values) # html diff

#----------------------------[relstate]
def relstate():
    return rel_state

#----------------------------[relupdate]
def relupdate(val):
    global rel_state

    rel_state = val
    GPIO.relay(rel_state)
    return

#----------------------------[gethtmltable]
def gethtmltable():
    html  = "<tt><table>"
    html += "<tr align='left'><th>Raum</th><th>Temperatur  </th><th>Luftfeuchtigkeit</th></tr>"
    html += "<tr><td>Obergescho&szlig;</td><td>{:>5s} &deg;C {:s}</td><td>{:>5s} % {:s}</td></tr>".format(values[0], hcode[0], values[ 9], hcode[ 9])
    html += "<tr><td>Halle            </td><td>{:>5s} &deg;C {:s}</td><td>{:>5s} % {:s}</td></tr>".format(values[1], hcode[1], values[10], hcode[10])
    html += "<tr><td>Schlafzimmer     </td><td>{:>5s} &deg;C {:s}</td><td>{:>5s} % {:s}</td></tr>".format(values[2], hcode[2], values[11], hcode[11])
    html += "<tr><td>Toilette         </td><td>{:>5s} &deg;C {:s}</td><td>{:>5s} % {:s}</td></tr>".format(values[3], hcode[3], values[12], hcode[12])
    html += "<tr><td>Badezimmer       </td><td>{:>5s} &deg;C {:s}</td><td>{:>5s} % {:s}</td></tr>".format(values[4], hcode[4], values[13], hcode[13])
    html += "<tr><td>K&uuml;che       </td><td>{:>5s} &deg;C {:s}</td><td>{:>5s} % {:s}</td></tr>".format(values[5], hcode[5], values[14], hcode[14])
    html += "<tr><td>Heizung          </td><td>{:>5s} &deg;C {:s}</td><td>{:>5s} % {:s}</td></tr>".format(values[6], hcode[6], values[15], hcode[15])
    html += "<tr><td>B&uuml;ro        </td><td>{:>5s} &deg;C {:s}</td><td>{:>5s} % {:s}</td></tr>".format(values[7], hcode[7], values[16], hcode[16])
    html += "<tr><td>Au&szlig;en      </td><td>{:>5s} &deg;C {:s}</td><td>{:>5s} % {:s}</td></tr>".format(values[8], hcode[8], values[17], hcode[17])
    html += "</table></tt><p>"
    html = html.replace(" ", "&nbsp;")
    if relstate() == 1:
        html += "Heizung ist ein<br>"
    else:
        html += "Heizung ist aus<br>"
    return html

#----------------------------[once_a_hour]
def once_a_hour():
    log.info("main", "once_a_hour")
    log.line(line)
    return

#----------------------------[once_a_day]
def once_a_day(sendmail):
    global lval
    global hcode
    global diff

    log.info("main", "once_a_day")

    # calculate diff
    try:
        for i in range(16+2):
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
    except Exception as ex:
        log.info("main", "error calculate diff: {:s}".format(str(ex)))
        log.info("main", str(values))
        log.info("main", str(lval))

    # send mail
    if sendmail == 1:
        mail.send(gethtmltable())
    return

#----------------------------[analyze]
def analyze(newline):
    global values
    global line

    # format and split
    line = newline
    line = line.replace("$1;1;;", "")
    line = line.replace(',', '.')
    values = line.split(";")

    # readdht
    dht22 = DHT.read()
    print(dht22)
    values.insert(8,  dht22[1])
    values.insert(17, dht22[0])

    # format
    try:
        for i in range(16+2):
            if values[i] != "?":
                xval = float(values[i])
                xstr = "{:3.1f}".format(xval)
                values[i] = xstr
    except Exception:
        pass

    # output
    print(time.strftime("%d-%m-%Y Time: %H:%M:%S",time.localtime()))
    print("Obergeschoß  {:>5s} °C {:s}   {:>5s} % {:>s}".format(values[0], diff[0], values[ 9], diff[ 9]))
    print("Halle        {:>5s} °C {:s}   {:>5s} % {:>s}".format(values[1], diff[1], values[10], diff[10]))
    print("Schlafzimmer {:>5s} °C {:s}   {:>5s} % {:>s}".format(values[2], diff[2], values[11], diff[11]))
    print("Toilette     {:>5s} °C {:s}   {:>5s} % {:>s}".format(values[3], diff[3], values[12], diff[12]))
    print("Badezimmer   {:>5s} °C {:s}   {:>5s} % {:>s}".format(values[4], diff[4], values[13], diff[13]))
    print("Küche        {:>5s} °C {:s}   {:>5s} % {:>s}".format(values[5], diff[5], values[14], diff[14]))
    print("Heizung      {:>5s} °C {:s}   {:>5s} % {:>s}".format(values[6], diff[6], values[15], diff[15]))
    print("Büro         {:>5s} °C {:s}   {:>5s} % {:>s}".format(values[7], diff[7], values[16], diff[16]))
    print("Außen        {:>5s} °C {:s}   {:>5s} % {:>s}".format(values[8], diff[8], values[17], diff[17]))
    return

#----------------------------[run_test]
def run_test():
    global lval

    # dht
    dht22 = DHT.read()
    print (dht22)
    # check line with ?
    analyze("$1;1;;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?;?")
    once_a_hour()
    once_a_day(0)
    # check received line
    analyze("$1;1;;10,1;20,2;30,3;40,4;50,5;60,6;70,7;80,8;90,9;10,1;11,2;12,3;13,4;14,5;15,6;16,7")
    once_a_hour()
    once_a_day(0)
    # check diffs
    lval = list(values)
    lval[0] = "8.8"
    lval[1] = "22.5"
    once_a_hour()
    once_a_day(0)
    analyze("$1;1;;10,1;20,2;30,3;40,4;50,5;60,6;70,7;80,8;90,9;10,1;11,2;12,3;13,4;14,5;15,6;16,7")
    return

#----------------------------[checkarguments]
def checkarguments():
    global lval

    if len(sys.argv) != 2:
        return

    if sys.argv[1] == "debug":
        run_test()
        time.sleep(2)
        webserver.stop()
        log.info("main", "exit (debug)")
        GPIO.cleanup()
        exit()
    if sys.argv[1] == "fakeval":
        analyze("$1;1;;10,1;20,2;30,3;40,4;50,5;60,6;70,7;80,8;90,9;10,1;11,2;12,3;13,4;14,5;15,6;16,7")
        lval = list(values)
        lval[0] = "8.8"
        lval[1] = "22.5"
        once_a_hour()
        once_a_day(0)
        analyze()

    return

#----------------------------[serial_init]
def serial_init():
    GPIO.usb_status(0)
    try:
        ser = serial.Serial("/dev/ttyUSB0", 9600)
        log.info("serial", "usb connected")
        GPIO.usb_status(1)
        return ser
    except SerialException:
        GPIO.usb_blink(0)
        time.sleep(5)
        return None

#----------------------------[main]
def main():
    # init
    GPIO.init()
    webserver.start(gethtmltable, relstate, relupdate, GPIO.tcp_status)
    schedule.every().day.at("08:00").do(once_a_day, 1)
    schedule.every().hour.do(once_a_hour)

    # arguments
    checkarguments()

    # running
    ser = None
    while True:
        if ser == None:
            ser = serial_init()
        else:
            if not ser.isOpen():
                ser = serial_init()
            else:
                newline = str(ser.readline(), "utf-8")
                analyze(newline)
                GPIO.usb_blink(1)
        schedule.run_pending()

#----------------------------[]
if __name__=='__main__':
    try:
        log.info("main", "starting")
        main()
    except:
        GPIO.cleanup()
        webserver.stop()
        log.info("main", "exit")
