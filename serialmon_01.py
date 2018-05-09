#!/usr/bin/python3 -u

import serial,sys,os

# serial port of USB-WDE1

port = '/dev/ttyUSB0'

# MAIN

def main():
  # open serial line
  ser = serial.Serial(port,9600)
  if not ser.isOpen():
    print ("Unable to open serial port %s") % port
    sys.exit(1)
  print ("connected: " + port)

  while True:
   
                             # read line from WDE1
   line = ser.readline()
   #print (line)
   line = line.strip(b"$1;1;;")
   print (line)
   #ln1 = line[0:6]           # Slice
   #ln1 = line.partition(b";")
   
   line = (line.split(b";"))  # Data is a bytes object !!! Therefore b
   #for i in range(0,8):      # Resuts in a Tuple
      #print (line[i])
   print (b"Obergesch " + line[0] + b" C  " + line[8] + b" %")
   print (b"Halle     " + line[1] + b" C  " + line[9] + b" %")
   print (b"Schlafzi  " + line[2] + b" C  " + line[10] + b" %")
   print (b"Toilette  " + line[3] + b" C  " + line[11] + b" %")
   print (b"Badezi    " + line[4] + b" C  " + line[12] + b" %")
   print (b"Kueche    " + line[5] + b" C  " + line[13] + b" %")
   print (b"Heizung   " + line[6] + b" C  " + line[14] + b" %")
   print (b"Buero     " + line[7] + b" C  " + line[15] + b" %")
   
if __name__=='__main__':

   main()


