#!/usr/bin/python3 -u

import serial
import sys
import os

port = '/dev/ttyUSB0'     # serial port of USB-WDE1

#----------------------------[analyze]
def analyze(line):
    line = line.strip(b"$1;1;;")
    print (line)
    line = (line.split(b";"))   # Data is a bytes object !!! Therefore b
    print (b"Obergesch " + line[0] + b" C    " + line[ 8] + b" %")
    print (b"Halle     " + line[1] + b" C    " + line[ 9] + b" %")
    print (b"Schlafzi  " + line[2] + b" C    " + line[10] + b" %")
    print (b"Toilette  " + line[3] + b" C    " + line[11] + b" %")
    print (b"Badezi    " + line[4] + b" C    " + line[12] + b" %")
    print (b"Kueche    " + line[5] + b" C    " + line[13] + b" %")
    print (b"Heizung   " + line[6] + b" C    " + line[14] + b" %")
    print (b"Buero     " + line[7] + b" C    " + line[15] + b" %")
    return

#----------------------------[main]
def main():
    ser = serial.Serial(port,9600)  # open serial line        
    if not ser.isOpen():
        print ("Unable to open serial port %s") % port
        sys.exit(1)
    print ("connected: " + port)

    while True:
        line = ser.readline()       # read line from WDE1
        analyze(line)
     
#----------------------------[]     
if __name__=='__main__':
    #analyze("$1;1;;30;31;32;33;34;35;36;37;50;51;52;53;54;55;56;57")
    main()
