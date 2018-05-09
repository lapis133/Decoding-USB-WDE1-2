#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import schedule
import smtplib
import serial
import time
import sys
import os

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

#----------------------------[main]
def main():
    ser = serial.Serial(port,9600)  # open serial line        
    if not ser.isOpen():
        print ("Unable to open serial port %s") % port
        sys.exit(1)
    print ("connected: " + port)

    schedule.every().day.at("08:00").do(once_a_day)

    while True:
        schedule.run_pending()      # check clock
        line = ser.readline()       # read line from WDE1
        analyze(line)               # analyze

#----------------------------[main]
def test():
    line = "$1;1;;30;31;32;33;34;35;36;37;50;51;52;53;54;55;56;57"
    analyze(line)
    once_a_day()
    
#----------------------------[]     
if __name__=='__main__':
    main()
    #test()
