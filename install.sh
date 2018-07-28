#!/bin/bash
sudo cp -n serialmon_01.ini /usr/local/etc
#sudo cp serialmon_01.pem /usr/local/etc
sudo mkdir /usr/local/bin/serialmon
sudo cp *.py /usr/local/bin/serialmon
sudo cp *.log /usr/local/bin/serialmon
sudo chmod +x /usr/local/bin/serialmon/serialmon_01.py
sudo chmod +x /usr/local/bin/serialmon/serialmon_sensor.py
#sudo rm /var/log/serialmon_info.log
