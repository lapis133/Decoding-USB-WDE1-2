#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import schedule
import serial
import time
import sys
import os

port = '/dev/ttyUSB0'     # serial port of USB-WDE1

#----------------------------[once_a_day]
def once_a_day():
    print ("once_a_day")
    return

#----------------------------[analyze]
def analyze(line):
    line = line.strip("$1;1;;")
    print (line)
    line = (line.split(";"))
    print ("Obergesch " + line[0] + "°C    " + line[ 8] + " %")
    print ("Halle     " + line[1] + "°C    " + line[ 9] + " %")
    print ("Schlafzi  " + line[2] + "°C    " + line[10] + " %")
    print ("Toilette  " + line[3] + "°C    " + line[11] + " %")
    print ("Badezi    " + line[4] + "°C    " + line[12] + " %")
    print ("Kueche    " + line[5] + "°C    " + line[13] + " %")
    print ("Heizung   " + line[6] + "°C    " + line[14] + " %")
    print ("Buero     " + line[7] + "°C    " + line[15] + " %")
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
        #line = "$1;1;;30;31;32;33;34;35;36;37;50;51;52;53;54;55;56;57"
        analyze(line)               # analyze
        #time.sleep(5)

#----------------------------[]     
if __name__=='__main__':
    main()
