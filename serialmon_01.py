#!/usr/bin/python3 -u
#!-*- coding: utf-8 -*-
# 21.05.2018
import time,smtplib,serial,sys,os

# serial port of USB-WDE1

port = '/dev/ttyUSB0'

#------------------------------------------[serial_init]
def serial_init():
  global ser
  global line
  ser = serial.Serial(port,9600)       # open serial line
  if not ser.isOpen():
    print ("Unable to open serial port %s") % port
    sys.exit(1)
  print ("connected: " + port)
  return
#--------------------------------------------[ End ]
  while True:
                    
   line = ser.readline()      # read line from WDE1
   print (line)   
   line = line.strip(b"$1;1;;")
#   print (line)
#   values = repr (line)   
   values = (line.split(b";"))  # Data is a bytes object !!! Therefore b
  return
#------------------------------------------[analyze(line)]
def analyse(line):
   global values

   line = line.strip(b"$1;1;;")
#   print (line)
#   values = repr (line)   
   values = (line.split(b";"))  # Data is a bytes object !!! Therefore b
   
   print (b"Obergesch " + values[0] + b"°C  " + values[8] + b" %")
   print (b"Halle     " + values[1] + b"°C  " + values[9] + b" %")
   print (b"Schlafzi  " + values[2] + b" C  " + values[10] + b" %")
   print (b"Toilette  " + values[3] + b" C  " + values[11] + b" %")
   print (b"Badezi    " + values[4] + b" C  " + values[12] + b" %")
   print (b"Kueche    " + values[5] + b" C  " + values[13] + b" %")
   print (b"Heizung   " + values[6] + b" C  " + values[14] + b" %")
   print (b"Buero     " + values[7] + b" C  " + values[15] + b" %")
   print ()
   return
#--------------------------------------------[ End ]

#--------------------------------------------[ Show Time ]
def showtime():
  global lt

  lt = time.localtime()   # aktuelle zeit als Tupel
  stunde, minute, sekunde = lt[3:6]
  print(time.strftime("%d.%m.%Y Time: %H:%M:%S", lt))
  print()
  return
#--------------------------------------------[ End ]
  
# MAIN

def main():

    serial_init()

    while True:
                               
     line = ser.readline()   # read line from WDE1
     #print (line)   
#     print(b"\033[H\033]J")
     showtime()
     analyse(line)
   
   
if __name__=='__main__':

   main()


