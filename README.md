# Decoding-USB-WDE1-2
The incoming string looks like this:
```
$1;1; ;25,9; ;23,8;24,4;24,8;25,4;23,6;23,2;54; ;61;61;60;58;63;63; ; ; ; ; ;0
```
Programm logging is found in /var/log/serialmon_info.log and the received lines in /var/log/serialmon_01.log

## Preparation
```
sudo apt-get install python3-serial python3-rpi.gpio python3-pip
sudo pip3 install schedule
```

If using DHT22:
```
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
sudo python serialmon_dht22.py
```
or
```
sudo python serialmon_dht22.py &
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
2   4   6   8   10  12  14  16  18  20  22  24  26  28  30  32  34  36  38  40
1   3   5   7   9   11  13  15  17  19  21  23  25  27  29  31  33  35  37  39
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
sudo chmod +x install.sh
./install.sh
```
for email notification fill the variables in /usr/local/etc/serialmon_01.ini

add in /etc/rc.local before the last line (exit 0):
```
/usr/local/bin/serialmon_dht22.py &
/usr/local/bin/serialmon_01.py &
```

**If using DS1820:**

add in #/etc/modules
```
w1-gpio pullup=1
w1-therm
```

add in /boot/config.txt
```
dtoverlay=w1-gpio,gpiopin=4
```
