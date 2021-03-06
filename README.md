# Home temperature observation

Key features of this project are:
* Decoding USB-WDE1-2
* Decoding DHT22
* Decoding DS1822
* LED status
* Temperature logging
* Email notification
* Webserver

Programm logging is found in /var/log/serialmon_info.log and the received lines in /var/log/serialmon_01.log

## Preparation
```
sudo apt-get update
sudo apt-get install python3-serial python3-rpi.gpio python3-pip
sudo pip3 install schedule
```

If using https:
```
openssl req -x509 -newkey rsa:2048 -keyout serialmon_01.pem -out serialmon_01.pem -days 730 -nodes -sha256 -subj "/CN=Decoding-USB-WDE1-2"
sudo chmod +r serialmon_01.pem
```

If using DHT22:
```
sudo apt-get update
sudo apt-get install build-essential python-dev python-setuptools

git clone https://github.com/adafruit/Adafruit_Python_DHT.git && cd Adafruit_Python_DHT
sudo python setup.py install
```

## Running
```
python3 serialmon_01.py
```
or
```
python3 serialmon_01.py debug
```
or
```
python3 serialmon_01.py fakeval
```
If already "installed" execute this before running from console:
```
ps -aux | grep  python3 /usr/local/bin/serialmon_01.py
sudo kill [pid]
```

**Running (DHT22)**
```
sudo python serialmon_sensor.py
```
or
```
sudo python serialmon_sensor.py &
```

## optional hardware layout
http://rpi.science.uoit.ca/lab/gpio/
```
                    USB-Status                              TCP-Status
                    +---+---+                               +---+---+
                    ^   |   ^                               ^   |   ^
                   LED  |  LED                             LED  |  LED
                  green |  red                             red  | green
                    ^   |   ^                               ^   |   ^
                   1k0  |  1k0                             1k0  |  1k0
                    |   |   |                               |   |   |
5V  5V  GND 8   10  12  GND 16  18  GND 22  24  26  28  GND 32  GND 36  38  40
3V3 3   5   7   GND 11  13  15  3V3 19  21  23  GND 27  29  31  33  35  37  GND
|           |   |   |           |    |          |                       |   |
|        +--+   |   |           +4k7-+    +-----+                      1k0  ^
|        |  |   |  REL          |    |    |                             |   |
|       4k7 |   |               P1   P2   P4                           LED  |
|        |  |   |                  DHT22                              DHT22 ^
+--------+  |   |                                                       |   |
         |  |   |                                                       +---+
         P3 P2 P1
          DS1820
```

## Installation
```
sudo ./install.sh
```
for email notification fill the variables in /usr/local/etc/serialmon_01.ini

add in /etc/rc.local before the last line (exit 0):
```
/usr/local/bin/serialmon/serialmon_sensor.py &
/usr/local/bin/serialmon/serialmon_01.py &
```

**If using DS1820:**

add in /etc/modules
```
w1-gpio pullup=1
w1-therm
```

add in /boot/config.txt
```
dtoverlay=w1-gpio,gpiopin=4
```
