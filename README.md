# Decoding-USB-WDE1-2
In the first step I want to make an eye friendly page in which Rooms and Temperatures are displayed. 
The incoming string looks like this:
$1;1; ;25,9; ;23,8;24,4;24,8;25,4;23,6;23,2;54; ;61;61;60;58;63;63; ; ; ; ; ;0

## Preparation
* sudo apt-get install python-serial python3-serial python-rpi.gpio python3-rpi.gpio python-schedule python3-schedule

add in ~/.bashrc:
* export SERIALMON_SMPT_HOST=
* export SERIALMON_SMPT_PORT=
* export SERIALMON_SMPT_EMAIL=
* export SERIALMON_SMPT_PASSWORD=
* export SERIALMON_DESTINATION_EMAIL=

### optional hardware layout
http://rpi.science.uoit.ca/lab/gpio/
```
                    +---+---+                               +---+---+ 
                    ^   |   ^                               ^   |   ^ 
                   LED  |  LED                             LED  |  LED 
                  green |  red                             red  | green 
                    ^   |   ^                               ^   |   ^ 
                   1k0  |  1k0                             1k0  |  1k0 
                    |   |   |                               |   |   | 
2   4   6   8   10  12  14  16  18  20  22  24  26  28  30  32  34  36  38  40
1   3   5   7   9   11  13  15  17  19  21  23  25  27  29  31  33  35  37  39
```

## Installation
* sudo cp serialmon_01.py /usr/local/bin
* sudo chmod +x /usr/local/bin/serialmon_01.py

add in /etc/rc.local before the last line (exit 0):
* /usr/local/bin/serialmon_01.py &
